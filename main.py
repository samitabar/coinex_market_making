import time

from coinex import Coinex

import helper as hp


client = Coinex("TEST", "TEST2")


def find_best_markets():
    data = client.all_market_stats()
    a = client.market_transaction_info()

    desired_markets = []

    for market in data["data"]["ticker"]:
        if market[-4:] == "USDT" and float(data["data"]["ticker"][market]["vol"]) * float(
                data['data']['ticker'][market]['sell']) > 500000:
            if not bool(a[market]["is_amm_market"]):
                buy = float(data['data']['ticker'][market]['buy'])
                sell = float(data['data']['ticker'][market]['sell'])
                diff = float(sell) - float(buy)
                gap = (diff / buy) * 100
                if gap > 0.05:
                    desired_markets.append(market)
                print(f"Gap {market} : {round(gap, 2)}% ")
            else:
                pass
        else:
            pass
    return desired_markets

def buy_func():
    balance = client.balance_info(CONFIG.coin.upper())
    current_total_balance = round(float(balance["frozen"]) + float(balance["available"]), CONFIG.qty_round_from)

    all_open_buy_orders = client.open_orders_by_side(CONFIG.coin.upper()+"USDT", side="buy").get("data")

    if len(all_open_buy_orders) == 0:
        orderbook = client.market_depth(CONFIG.coin.upper()+"USDT")
        current_gap_percent = hp.gap_calc(orderbook)

        if current_gap_percent > CONFIG.gap_percent_to_start:
            top_10_buyers = orderbook["bids"][:10]
            new_buy_price = hp.best_price_finder(
                top_10_buyers,
                minimum=CONFIG.min_total_price,
                min_delta=CONFIG.minimum_delta
            ) + CONFIG.go_over_top

            new_buy_price = round(new_buy_price, CONFIG.price_round_from)

            amount = round((CONFIG.base_balance + CONFIG.amount_to_deal - current_total_balance), CONFIG.qty_round_from)

            if amount > CONFIG.minimum_coin:
                result = client.place_limit_order(market=f"{CONFIG.coin}USDT",
                                                  side="buy",
                                                  amount=amount,
                                                  price=new_buy_price)
                print(f'BUY -> {result}')

            else:
                print(f'BUY -> amount < CONFIG.minimum_coin | {amount} < {CONFIG.minimum_coin}')
                return

        else:
            print(f'BUY -> current_gap_percent < CONFIG.gap_percent_to_start | '
                  f'{current_gap_percent} < {CONFIG.gap_percent_to_start}')
    else:
        print(f'BUY -> len(all_open_buy_orders) != 0 | {len(all_open_buy_orders)=}')


def sell_func():
    balance = client.balance_info(CONFIG.coin.upper())
    current_available_balance = round(float(balance["available"]), CONFIG.qty_round_from)

    if current_available_balance >= CONFIG.base_balance + CONFIG.minimum_coin:
        orderbook = client.market_depth(CONFIG.coin.upper() + "USDT")
        top_10_seller = orderbook["asks"][:10]
        new_sell_price = hp.best_price_finder(
            top_10_seller,
            minimum=CONFIG.min_total_price,
            min_delta=CONFIG.minimum_delta
        ) - CONFIG.go_over_top
        new_sell_price = round(new_sell_price, CONFIG.price_round_from)

        amount = round((current_available_balance - CONFIG.base_balance), CONFIG.qty_round_from)

        if amount > CONFIG.minimum_coin:
            result = client.place_limit_order(market=f"{CONFIG.coin}USDT", side="sell", amount=amount, price=new_sell_price)
            print(f'SELL -> {result}')
        else:
            print(f'SELL -> amount < CONFIG.minimum_coin | {amount} < {CONFIG.minimum_coin}')
    else:
        print(f'SELL -> current_available_balance <= CONFIG.base_balance + CONFIG.minimum_coin | '
              f'{current_available_balance} <= {CONFIG.base_balance} + { CONFIG.minimum_coin}')


def cancel_buy():
    all_open_order = client.open_orders_by_side(f"{CONFIG.coin}USDT", side="buy").get("data")
    if len(all_open_order) > 0:
        orderbook = client.market_depth(CONFIG.coin.upper() + "USDT")
        current_gap_percent = hp.gap_calc(orderbook)
        for order in all_open_order:
            my_order_price = order.get("price")
            my_order_id = order.get("id")

            above_mine = hp.calc_above_mine_offline_with_list(str(my_order_price), orderbook["bids"])
            my_order_place = hp.find_my_order_offline(my_order_price, orderbook["bids"])
            below_me = orderbook["bids"][my_order_place:]
            delta = hp.delta_between_orders(below_me)[:5]
            first_delta = delta[0]

            if above_mine > CONFIG.min_total_price:
                cancel = client.cancel_order(id_=my_order_id, market=f"{CONFIG.coin}USDT")
                print(f'cancel_buy -> [above_mine] | {above_mine} < {CONFIG.min_total_price} | {cancel}')
                continue
            elif current_gap_percent <= CONFIG.gap_percent_to_start:
                cancel = client.cancel_order(id_=my_order_id, market=f"{CONFIG.coin}USDT")
                print(f'cancel_buy -> [current_gap_percent] | {current_gap_percent} < {CONFIG.gap_percent_to_start} | {cancel}')
                continue
            elif first_delta > CONFIG.go_over_top:
                cancel = client.cancel_order(id_=my_order_id, market=f"{CONFIG.coin}USDT")
                print(f'cancel_buy -> [first_delta] | {first_delta} < {CONFIG.go_over_top} | {cancel}')
                continue


def cancel_sell():
    all_open_order = client.open_orders_by_side(f"{CONFIG.coin}USDT", side="sell").get("data")
    if len(all_open_order) > 0:
        orderbook = client.market_depth(CONFIG.coin.upper() + "USDT")

        for order in all_open_order:
            my_order_price = order.get("price")
            my_order_id = order.get("id")

            above_mine = hp.calc_above_mine_offline_with_list(str(my_order_price), orderbook["asks"])
            my_order_place = hp.find_my_order_offline(my_order_price, orderbook["asks"])
            below_me = orderbook["asks"][my_order_place:]
            delta = hp.delta_between_orders(below_me)[:5]
            first_delta = delta[0]

            if above_mine > CONFIG.min_total_price:
                cancel = client.cancel_order(id_=my_order_id, market=f"{CONFIG.coin}USDT")
                print(f'cancel_sell -> [above_mine] | {above_mine} < {CONFIG.min_total_price} | {cancel}')
                continue
            elif first_delta > CONFIG.go_over_top:
                cancel = client.cancel_order(id_=my_order_id, market=f"{CONFIG.coin}USDT")
                print(f'cancel_sell -> [first_delta] | {first_delta} < {CONFIG.go_over_top} | {cancel}')
                continue


def main():
    if CONFIG.buy_status is True:
        try:
            buy_func()
        except Exception as e:
            print(e)
            pass
    try:
        cancel_buy()
    except Exception as e:
        print(e)
        pass

    if CONFIG.sell_status is True:
        try:
            sell_func()
        except Exception as e:
            print(e)
            pass

    try:
        cancel_sell()
    except Exception as e:
        print(e)
        pass

    time.sleep(10)

    print('---------- [#] ----------')


if __name__ == '__main__':
    CONFIG = hp.Config(1, coin="CET", buy_status=True, sell_status=True, min_total_price=15,
                       amount_to_deal=65, gap_percent_to_start=0.000001,
                       base_balance=340, minimum_coin=15, minimum_delta=0.000005, go_over_top=0.000001,
                       price_round_from=6, qty_round_from=1)
    while True:
        main()
