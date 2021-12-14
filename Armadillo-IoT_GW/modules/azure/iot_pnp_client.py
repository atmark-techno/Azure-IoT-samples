import asyncio
import certifi
import json
import os
import platform
import subprocess
from enum import IntEnum

from azure.iot.device import X509
from azure.iot.device import Message, MethodResponse
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device.exceptions import CredentialError

from modules.azure.model_config_base import ModelConfigBase
from modules.azure.model_dev_base import ModelDevBase

class ErrorCode(IntEnum):
    Success = 1,
    AuthenticationFailed = 2,
    ConnectionFailed = 3

class IoTPnPClient:
    def __init__(self, modelConfig, modelDev):
        self._modelConfig  = modelConfig
        self._modelDev     = modelDev
        self._clientHandle = None
        self._isConnected  = False
        self._doReconnect  = False
        if platform.system() == "Linux":
            debian_version = subprocess.getoutput(
                "cat /etc/os-release | grep VERSION_ID | sed -e 's/\"//g' | cut -c 12-"
            )
            if int(debian_version) >= 10:
                os.environ["SSL_CERT_FILE"] = certifi.where()

    def is_connected(self):
        return self._isConnected

    def process_alarm(self, alarm):
        return self._modelDev.process_alarm(alarm)

    async def auth_and_connect(self):
        if self._isConnected:
            return

        model_id  = self._modelDev.model_id()
        auth_conf = self._modelConfig.auth_props()

        print ("auth.mode", auth_conf[ModelConfigBase.IOTHUB_DEVICE_DPS_AUTH_MODE] )
        if self._modelConfig.is_x509_mode():
            x509 = X509(
                cert_file=auth_conf[ModelConfigBase.IOTHUB_DEVICE_DPS_X509_CERT],
                key_file=auth_conf[ModelConfigBase.IOTHUB_DEVICE_DPS_X509_KEY],
                pass_phrase=auth_conf[ModelConfigBase.IOTHUB_DEVICE_DPS_X509_PASS],
            )
            provisioning_device_client = ProvisioningDeviceClient.create_from_x509_certificate(
                provisioning_host=auth_conf[ModelConfigBase.IOTHUB_DEVICE_DPS_ENDPOINT],
                registration_id=auth_conf[ModelConfigBase.IOTHUB_DEVICE_DPS_DEVICE_ID],
                id_scope=auth_conf[ModelConfigBase.IOTHUB_DEVICE_DPS_ID_SCOPE],
                x509=x509,
            )
        else:
            provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
                provisioning_host=auth_conf[ModelConfigBase.IOTHUB_DEVICE_DPS_ENDPOINT],
                registration_id=auth_conf[ModelConfigBase.IOTHUB_DEVICE_DPS_DEVICE_ID],
                id_scope=auth_conf[ModelConfigBase.IOTHUB_DEVICE_DPS_ID_SCOPE],
                symmetric_key=auth_conf[ModelConfigBase.IOTHUB_DEVICE_DPS_DEVICE_KEY]
            )
        provisioning_device_client.provisioning_payload = {
            "modelId": model_id
        }
        try:
            registration_result = await provisioning_device_client.register()
            if registration_result.status != "assigned":
                print("Could not provision device.")
                return ErrorCode.AuthenticationFailed
            else:
                print("Device was assigned")
        except:
            print("Connection error.")
            return ErrorCode.ConnectionFailed

        registration_state = registration_result.registration_state
        print(registration_state.assigned_hub)
        print(registration_state.device_id)
        if self._modelConfig.is_x509_mode():
            x509 = X509(
                cert_file=auth_conf[ModelConfigBase.IOTHUB_DEVICE_DPS_X509_CERT],
                key_file=auth_conf[ModelConfigBase.IOTHUB_DEVICE_DPS_X509_KEY],
                pass_phrase=auth_conf[ModelConfigBase.IOTHUB_DEVICE_DPS_X509_PASS],
            )
            device_client = IoTHubDeviceClient.create_from_x509_certificate(
                x509=x509,
                hostname=registration_state.assigned_hub,
                device_id=registration_state.device_id,
                product_info=model_id,
                connection_retry=False
            )
        else:
            device_client = IoTHubDeviceClient.create_from_symmetric_key(
                symmetric_key=auth_conf[ModelConfigBase.IOTHUB_DEVICE_DPS_DEVICE_KEY],
                hostname=registration_state.assigned_hub,
                device_id=registration_state.device_id,
                product_info=model_id,
                connection_retry=False
            )
        await device_client.connect()
        twin = await device_client.get_twin()
        if 'desired' in twin:
            desiredProps = twin['desired']
            del (desiredProps)['$version']
            for name in iter(desiredProps):
                self._modelDev.set_prop(name, desiredProps[name])
        del (twin['reported'])['$version']
        props = self._modelDev.props()
        if props != twin['reported']:
            await device_client.patch_twin_reported_properties(props)
        device_client.on_method_request_received = self._method_request_handler
        device_client.on_twin_desired_properties_patch_received = self._twin_patch_handler
        device_client.on__message_received = self._message_received_handler
        self._clientHandle = device_client
        self._isConnected  = True

        return ErrorCode.Success

    async def disconnect(self):
        if self._isConnected:
            await self._clientHandle.disconnect()
            self._isConnected = False

    async def shutdown(self):
        await self.disconnect()
        await self._clientHandle.shutdown()

    async def send_telemetry(self, telemetry_data):
        if not self._isConnected:
            if self._doReconnect:
                print("try reconnect...")
                await self._do_connect()
                print("done")
            return False
        if "$.sub" in telemetry_data:
            component = telemetry_data["$.sub"]
            del telemetry_data["$.sub"]
        else:
            component = None
        msg = Message(json.dumps(telemetry_data))
        msg.content_enconding = "utf-8"
        msg.content_type      = "application/json"
        if component is not None:
            msg.custom_properties["$.sub"] = component
        print("Send message")
        try:
             await asyncio.wait_for(self._clientHandle.send_message(msg), timeout=10)
        except:
            print("caught an exception from send_message().")
            await self.disconnect()
            self._isConnected = False
            self._doReconnect = True
            return False

        return True

    async def send_updated_prop(self, prop_data):
        if not self._isConnected:
            return False
        try:
            await asyncio.wait_for(self._clientHandle.patch_twin_reported_properties(prop_data), timeout=10)
        except:
            print("connection has broken.")
            await self.disconnect()
            self._isConnected = False
            return False

        return True

    async def _do_connect(self):
        await self.auth_and_connect()

    async def _method_request_handler(self, method_request):
        post_proc = None
        (result, post_proc) = await self._modelDev.execute_commnad(
            method_request.name, method_request.payload)
        status = 400
        if not result:
            print("Could not execute the direct method: ", method_request.name)
            payload = {"result": False, "data": "unknown method"}
        else:
            payload = {
                "result": True,
                "data": (method_request.name + " is succeeded" if isinstance(result, bool) else result)
            }
            status = 200
        method_response = MethodResponse.create_from_method_request(
            method_request, status, payload
        )

        await asyncio.wait_for(self._clientHandle.send_method_response(method_response), timeout=10)
        if post_proc:
            post_proc()

    async def _twin_patch_handler(self, patch):
        ignore_keys = ["__t", "$version"]
        version = patch["$version"]
        props   = {}
        for name, value in patch.items():
            if not name in ignore_keys:
                new_value = self._modelDev.set_prop(name, value)
                props[name] = {
                    "ac": 200,
                    "ad": "Successfully executed patch",
                    "av": version,
                    "value": new_value
                }
        await asyncio.wait_for(self._clientHandle.patch_twin_reported_properties(props), timeout=10)

    async def _message_received_handler(self, msg):
        print("got message from the cloud, msg= ", msg)

#
# End of File
#

