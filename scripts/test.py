import operator

ops = {
    'AND': operator.and_,
    'OR': operator.or_
}

valueFromConfig = 'AND'

function = ops[valueFromConfig]
result = function()