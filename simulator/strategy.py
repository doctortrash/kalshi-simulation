from state import TradingState

POSITION_LIMIT = 40

class Strategy(): 

    def __init__(self, 
                 state: TradingState) -> None:
        self.state = state

    def kalshiUpdate(self) -> None: 
        orderbook = self.state.getOrderbook()
        if len(orderbook["bids"]) == 0 or len(orderbook["asks"]) == 0: 
            return
        
        best_bid = max(orderbook["bids"])
        best_ask = min(orderbook["asks"])
        mid = int((best_bid + best_ask) / 2)

        bid_vol = min(10, POSITION_LIMIT - self.state.position)
        ask_vol = min(10, POSITION_LIMIT + self.state.position)

        self.state.insertOrder("B", mid - 1, bid_vol)
        self.state.insertOrder("A", mid + 1, ask_vol)
        # self.state.insertOrder("B", 1, 1)
        # self.state.insertOrder("A", best_bid, 10)
        
    def spUpdate(self) -> None: 
        pass