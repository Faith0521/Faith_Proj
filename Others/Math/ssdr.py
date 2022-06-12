"""

"""
import numpy
def dot(list1, list2):
    """

    :param list1:
    :param list2:
    :return:
    """
    return sum([ele1*ele2 for ele1, ele2 in zip(list1, list2)])

def matrix_dot(matrix, list):
    """

    :param matrix:
    :param list:
    :return:
    """
    return [dot(list1,list) for list1 in matrix]

def sub_list(list1, list2):
    """

    :param list1:
    :param list2:
    :return:
    """
    return [ele1 - ele2 for ele1, ele2 in zip(list1, list2)]

def get_err(weights, data_x, data_y):
    """

    :param weights:
    :param ptA:
    :param ptB:
    :return:
    """
    err = sub_list(matrix_dot(data_x, weights), data_y)
    return dot(err, err)/len(err)

def liner_regression(data_x, data_y):
    """

    :param ptA:
    :param ptB:
    :return:
    """
    weights_length = len(data_x[0])
    weights = [1.0/weights_length]*weights_length
    for i in range(10):
        for weight_index in range(weights_length):
            other_weight_sum = 1.0 - weights[weight_index]
            if other_weight_sum < 0.0001:
                edit_scale_list = [-1.0/(weights_length-1)]*other_weight_sum
            else:
                edit_scale_list = [-weight/other_weight_sum for weight in weights]
            edit_scale_list[weight_index] = 1.0
            xs = matrix_dot(data_x, edit_scale_list)
            ys = sub_list(data_y, matrix_dot(data_x, weights))
            a = dot(xs, ys) / dot(xs, xs)
            weights = [weight + a*w for weight, w in zip(weights, edit_scale_list)]
            weights = [max(min(weight, 1.0), 0.0) for weight in weights]
            sum_weights = sum(weights)
            weights = [weight/sum_weights for weight in weights]
    return weights

def computeVertPos(self, vertexIndex, locator=None):
    






























