

def gen_server_order_id(user_uid, cl_order_id, ts, order_src='a'):
    return (order_src + format(ts, 'x')[-11:] + user_uid[-11:] + cl_order_id[-9:])[:32]
    """
    Server order generator based on user info and input.
    :param user_uid: user uid
    :param cl_order_id: user random digital and number id
    :param ts: order timestamp in milliseconds
    :param order_src: 'a' for rest api order, 's' for websocket order.
    :return: order id of length 32
    """

    return (order_src + format(ts, 'x')[-11:] + user_uid[-11:] + cl_order_id[-9:])[:32]


gen_server_order_id("U5843449924", "NUM6913", ts = 1586435683655)

 