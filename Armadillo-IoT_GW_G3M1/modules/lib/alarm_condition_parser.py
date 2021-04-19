from modules.lib.alarm_condition import AlarmCondition

def curried_binary_relation(type_a, value_a, relation):
    return lambda type_b, value_b: (
        type_a == type_b and relation(value_b, value_a)
    )


def parse_condition_expression(expr):
    values = expr.split(None, 2)
    if len(values) != 3:
        return None

    parsed = (
        values[2][1:-1] if values[2][0] in '\"\'' else
        float(values[2]) if "." in values[2] else
        int(values[2])
    )

    return (values[0], values[1], parsed)


operators_negation_table = {
    '<': '>=',
    '>': '<=',
    '<=': '>',
    '>=': '<',
    '==': '!=',
    '!=': '=='
}


def negate_operator(op):
    return operators_negation_table[op]


operators = {
    '<': lambda a, b: a < b,
    '>': lambda a, b: a > b,
    '<=': lambda a, b: a <= b,
    '>=': lambda a, b: a >= b,
    '==': lambda a, b: a == b,
    '!=': lambda a, b: a != b,
}


def str_to_hysteresis(str):
    if str is None:
        return 1

    hysteresis = 1
    try:
        hysteresis = int(str)
    except ValueError:
        return 1
    else:
        if hysteresis < 1:
            return 1
    return hysteresis


def parse_alarm_condition(alarm):
    alarm_type = alarm.get('type')
    description = alarm.get('description')
    generate_on = None
    generate_hysteresis = None
    if alarm.get('generate_on') is not None:
        generate_on = alarm.get('generate_on').get('condition')
        generate_hysteresis = alarm.get('generate_on').get('hysteresis')
    clear_on = None
    clear_hysteresis = None
    if alarm.get('clear_on') is not None:
        clear_on = alarm.get('clear_on').get('condition')
        clear_hysteresis = alarm.get('clear_on').get('hysteresis')

    if alarm_type is None or generate_on is None:
        raise Exception('Some required parameters are missing')

    parsed = parse_condition_expression(generate_on)
    if parsed is None:
        raise Exception('Failed to parse alarm conditions')

    operator = parsed[1]
    if operator not in operators:
        raise Exception('Invalid operator: {}'.format(operator))

    generate_on_lambda = curried_binary_relation(
        parsed[0],
        parsed[2],
        operators[parsed[1]],
    )

    if clear_on is None:
        clear_on_lambda = curried_binary_relation(
            parsed[0],
            parsed[2],
            operators[negate_operator(parsed[1])],
        )
    else:
        parsed = parse_condition_expression(clear_on)
        if parsed is None:
            raise Exception('Failed to parse alarm conditions')

        operator = parsed[1]
        if operator not in operators:
            raise Exception('Invalid operator: {}'.format(operator))

        clear_on_lambda = curried_binary_relation(
            parsed[0],
            parsed[2],
            operators[operator],
        )

    return AlarmCondition(
        alarm_type,
        description,
        generate_on_lambda,
        str_to_hysteresis(generate_hysteresis),
        clear_on_lambda,
        str_to_hysteresis(clear_hysteresis)
    )
