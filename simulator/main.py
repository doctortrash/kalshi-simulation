from state import TradingState
from strategy import Strategy
from new_strategy import CauchyStrategy
from simulator import Simulator

day = 10

if __name__ == "__main__":
    state = TradingState()
    strategy = CauchyStrategy(state)
    simulator = Simulator(f"../data/apr-{day}-combined.csv", state, strategy)
    simulator.simulate()