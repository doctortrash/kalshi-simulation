from state import TradingState
from strategy import Strategy
import pandas as pd

class Simulator(): 

    def __init__(self, 
                 fileName: str,
                 state: TradingState,
                 strat: Strategy) -> None:
        
        self.state = state
        self.data = pd.read_csv(fileName)
        self.strat = strat
        self.events = pd.DataFrame(columns=["Time", "PnL", "Position", "AdjPnL", "SP_Price"])
        self.last_adj_pnl = -1 
        self.counter = 0 

    def simulate(self) -> None: 
        
        priceMin = self.data["Price"].iloc[0]
        # Round priceMin down to the nearest 50
        priceMin = int(priceMin / 50) * 50

        priceMax = self.data["Price"].iloc[0]
        # Round priceMax up to the nearest 50
        priceMax = (int(priceMax / 50) * 50 + 50) - 0.01

        # Iterate through data
        for index, row in self.data.iterrows():
            # print(index)
            instrument = row["Instrument"]
            time = row["Time"]

            if instrument == 0: 
                self.state.updateSP(row["Price"])
                self.strat.spUpdate()
            elif instrument == 1: 
                operation = row["Operation"]
                price = int(row["Price"] / 100)
                side = row["Side"]
                volume = int(row["Volume"])

                if operation == "Insert": 
                    self.state.updateOrderbook(side, price, volume, "Insert", False)     
                elif operation == "Cancel": 
                    self.state.updateOrderbook(side, price, volume, "Cancel", False)
                
                if index + 1 < len(self.data) and self.data["Time"].iloc[index + 1] == row["Time"]:
                    continue

                newRow = [time, round(self.state.pnl, 2), self.state.position, self.state.pnl, self.state.sp_price]
                if self.state.position > 0 and self.state.sp_price >= priceMin and self.state.sp_price <= priceMax:
                    newRow[3] = self.state.pnl + self.state.position
                elif self.state.position < 0 and (self.state.sp_price < priceMin or self.state.sp_price > priceMax):
                    newRow[3] = self.state.pnl - self.state.position
                
                newRow[3] = round(newRow[3], 2)
                self.events.loc[len(self.events)] = newRow
                
                # if newRow[3] != self.last_adj_pnl or self.counter % 100 == 0: 
                #     self.events.loc[len(self.events)] = newRow
                #     self.last_adj_pnl = newRow[3]
                
                # self.counter += 1

                self.strat.kalshiUpdate()

        print("Simulation complete. Finished with posiiton of " + str(self.state.position) + " and SP of " + str(self.state.sp_price) + ".")
        marketResolution = True
        if self.state.sp_price >= priceMin and self.state.sp_price <= priceMax:
            print("Market resolved to YES")
            marketResolution = True
        else: 
            print("Market resolved to NO")
            marketResolution = False
        
        if self.state.position > 0 and marketResolution: 
            print(f"Settling {self.state.position} contracts at $1. Total PnL: ${self.state.pnl + self.state.position}")
        elif self.state.position > 0 and not marketResolution:
            print(f"Settling {self.state.position} contracts at $0. Total PnL: ${self.state.pnl}")
        elif self.state.position < 0 and marketResolution: 
            print(f"Settling {self.state.position} contracts at $0. Total PnL: ${self.state.pnl}")
        elif self.state.position < 0 and not marketResolution:
            print(f"Settling {self.state.position} contracts at $1. Total PnL: ${self.state.pnl - self.state.position}")
        
        # Write events to CSV
        self.events.to_csv("events.csv", index=True)


            