from state import TradingState
from strategy import Strategy
from simulator import Simulator

if __name__ == "__main__":
    state = TradingState()
    strategy = Strategy(state)
    simulator = Simulator("../data/apr-10-combined.csv", state, strategy)
    simulator.simulate()