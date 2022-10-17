import typing as t

MIN_VOLUME_TO_REMOVE = 15


class Config:
    def __init__(self, id_: int, coin: str, buy_status: bool, sell_status: bool,
                 min_total_price: t.Union[int, float], amount_to_deal: t.Union[int, float],
                 gap_percent_to_start: t.Union[int, float], base_balance: t.Union[int, float],
                 minimum_coin: t.Union[int, float],
                 minimum_delta: t.Union[int, float],
                 go_over_top: t.Union[int, float], price_round_from: int, qty_round_from: int):

        self.id = id_
        self.coin = coin
        self.buy_status = buy_status
        self.sell_status = sell_status
        self.min_total_price = min_total_price
        self.amount_to_deal = amount_to_deal
        self.gap_percent_to_start = gap_percent_to_start
        self.base_balance = base_balance
        self.minimum_coin = minimum_coin
        self.minimum_delta = minimum_delta
        self.go_over_top = go_over_top
        self.price_round_from = price_round_from
        self.qty_round_from = qty_round_from


def gap_calc(orderbook: t.Dict) -> t.Union[float, int] :
    bid_list = orderbook["bids"]
    ask_list = orderbook["asks"]
    sell_price = ask_list[0][0]
    buy_price = bid_list[0][0]
    diff = float(sell_price) - float(buy_price)
    gap_percent = (diff / float(buy_price)) * 100
    return gap_percent


def delta_between_orders(list_: list) -> list:
    _ = [int(float(x[0])) for x in list_]
    return [abs(j - i) for i, j in zip(_[:-1], _[1:])]


def cap_calc_offline(list_):
    obj: dict
    total = 0
    for obj in list_:
        total += float(obj[0]) * float(obj[1])

    return total


def calc_above_mine_offline_with_list(my_order: str, orders_list: list):
    my_order = float(str(my_order).replace(',', ''))
    response = orders_list

    i = 0
    for x in response:
        if float(x[0]) == my_order:
            break
        else:
            i += 1
    return cap_calc_offline(response[:i])


def best_price_with_sum_offline(bid_list: list, minimum: t.Union[float, int]) -> int:
    i = 0
    total_price = 0.0

    while total_price <= minimum:
        total_price += float(float(bid_list[i][0])) * float(bid_list[i][1])
        if total_price > minimum:
            break
        i += 1

    best_price = bid_list[i][0]

    return float(best_price)


def find_my_order_offline(my_order: str, target_order_book: t.List):
    my_order = float(str(my_order).replace(',', ''))
    i = 0

    for x in target_order_book:
        if float(x[0]) == my_order:
            return i
        else:
            i += 1


def best_price_finder(top_10_orderbook: t.List, minimum: t.Union[int, float], min_delta: t.Union[float, int]):
    best_price = None

    for order in top_10_orderbook:
        if float(order[0]) * float(order[1]) < MIN_VOLUME_TO_REMOVE:
            top_10_orderbook.remove(order)

    delta = delta_between_orders(top_10_orderbook)[:5]
    delta_sorted = sorted(delta, reverse=True)
    highest_delta = delta_sorted[0]
    
    if highest_delta >= min_delta:
        highest_delta_index = delta.index(highest_delta) + 1
        upper_order_book = top_10_orderbook[highest_delta_index:]

        for order in upper_order_book:
            if float(order[0]) * float(order[1]) >= minimum:
                best_price = order[0]
                break

        if calc_above_mine_offline_with_list(str(best_price), top_10_orderbook) >= minimum:
            return best_price_with_sum_offline(top_10_orderbook, minimum)

        return float(best_price)

    else:
        return best_price_with_sum_offline(top_10_orderbook, minimum)

