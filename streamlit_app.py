import random
import math
import time
from tabulate import tabulate
import os

class Project:
    def __init__(self, name, cost, life, annual_cash_flow, real_option, risk_level, user_gain):
        self.name = name
        self.cost = cost
        self.life = life
        self.annual_cash_flow = annual_cash_flow
        self.real_option = real_option
        self.risk_level = risk_level
        self.user_gain = user_gain
        self.owner = None
        self.purchase_round = None

    def calculate_npv(self, discount_rate=0.10):
        """Calculate Net Present Value of the project"""
        npv = -self.cost
        for year in range(1, self.life + 1):
            npv += self.annual_cash_flow / ((1 + discount_rate) ** year)
        return npv

    def calculate_irr(self):
        """Calculate Internal Rate of Return"""
        # Simple IRR approximation
        return (self.annual_cash_flow * self.life - self.cost) / (self.cost * self.life)

    def calculate_payback_period(self):
        """Calculate Payback Period"""
        return self.cost / self.annual_cash_flow

    def calculate_profitability_index(self, discount_rate=0.10):
        """Calculate Profitability Index"""
        present_value = 0
        for year in range(1, self.life + 1):
            present_value += self.annual_cash_flow / ((1 + discount_rate) ** year)
        return present_value / self.cost

class FinancingOption:
    def __init__(self, name, description, max_amount, conditions, impact):
        self.name = name
        self.description = description
        self.max_amount = max_amount
        self.conditions = conditions
        self.impact = impact  # Function or description of impact on player

class Event:
    def __init__(self, name, description, impact):
        self.name = name
        self.description = description
        self.impact = impact  # Function to apply event impact

class Tile:
    def __init__(self, position, name, tile_type, action=None):
        self.position = position
        self.name = name
        self.tile_type = tile_type  # "Investment", "Financing", "Event", "Neutral", "Special"
        self.action = action  # Associated project, financing, or event

class Player:
    def __init__(self, name, starting_cash=100):
        self.name = name
        self.cash = starting_cash  # Starting with $100M
        self.users = 1  # Starting with 1M users
        self.position = 0
        self.projects = []
        self.financing_history = []
        self.debt = 0
        self.equity_dilution = 0
        self.vc_funding_used = False
        self.ipo_done = False
        self.skip_next_turn = False

    def calculate_total_npv(self, current_round):
        """Calculate total NPV of all projects"""
        total_npv = 0
        for project in self.projects:
            # Calculate remaining cash flows based on when project was purchased
            remaining_life = project.life - (current_round - project.purchase_round)
            if remaining_life > 0:
                npv = 0
                for year in range(1, remaining_life + 1):
                    npv += project.annual_cash_flow / ((1 + 0.10) ** year)
                total_npv += npv

        # Apply equity dilution if any
        total_npv *= (1 - self.equity_dilution)

        # Apply IPO penalty if done
        if self.ipo_done:
            total_npv *= 0.7  # 30% NPV penalty for IPO

        return total_npv

    def can_afford(self, amount):
        """Check if player can afford a purchase"""
        return self.cash >= amount

    def pay(self, amount):
        """Pay an amount"""
        if self.can_afford(amount):
            self.cash -= amount
            return True
        return False

    def receive(self, amount):
        """Receive an amount"""
        self.cash += amount

    def add_users(self, count):
        """Add users"""
        self.users += count

    def lose_users(self, count):
        """Lose users"""
        self.users = max(0, self.users - count)

    def add_project(self, project, current_round):
        """Add a project to player's portfolio"""
        project.owner = self
        project.purchase_round = current_round
        self.projects.append(project)

    def add_financing(self, financing, amount):
        """Add financing to player's history"""
        self.financing_history.append((financing, amount))

        if financing.name == "Debt":
            self.debt += amount
        elif financing.name == "VC Funding":
            self.vc_funding_used = True
            self.equity_dilution += 0.10  # 10% NPV penalty
        elif financing.name == "Equity":
            self.equity_dilution += 0.20  # 20% NPV penalty
        elif financing.name == "IPO":
            self.ipo_done = True
            # IPO penalty applied in NPV calculation

    def pay_debt_interest(self):
        """Pay interest on debt"""
        interest = self.debt * 0.06  # 6% annual interest
        if self.can_afford(interest):
            self.cash -= interest
            return True
        return False

    def collect_project_revenues(self):
        """Collect revenues from all projects"""
        total_revenue = 0
        for project in self.projects:
            total_revenue += project.annual_cash_flow
        self.cash += total_revenue
        return total_revenue

class Finopoly:
    def __init__(self):
        self.players = []
        self.current_round = 1
        self.current_player_index = 0
        self.board = []
        self.projects = []
        self.financing_options = []
        self.events = []
        self.game_over = False

        self.initialize_game()

    def initialize_game(self):
        """Initialize game components"""
        self.create_projects()
        self.create_financing_options()
        self.create_events()
        self.create_board()

    def create_projects(self):
        """Create project cards"""
        self.projects = [
            Project("Expand to Asia Market", 50, 3, 20, "Expand", "High", 2),
            Project("Referral Program", 20, 3, 12, "Scale", "Low", 1.5),
            Project("Retail Partnership", 40, 3, 18, "User Trust", "High", 1.8),
            Project("AI Fraud Prevention", 30, 3, 15, "Efficiency Gain", "Medium", 1),
            Project("Product Launch", 35, 2, 25, "Rebrand", "Medium", 2.5),
            Project("Mobile App Redesign", 25, 2, 15, "User Experience", "Low", 1.2),
            Project("Blockchain Integration", 45, 3, 17, "Security", "High", 1.5),
            Project("Customer Support AI", 30, 2, 18, "Efficiency", "Medium", 0.8)
        ]

    def create_financing_options(self):
        """Create financing options"""
        self.financing_options = [
            FinancingOption("Debt", "Loan at 6% annual interest", 50, "Max $50M per round", "6% annual interest"),
            FinancingOption("VC Funding", "Raise $40M but lose 10% NPV", 40, "Once per game", "10% NPV dilution"),
            FinancingOption("Equity", "Raise capital but dilute 20% NPV", 60, "Once per round", "20% NPV dilution"),
            FinancingOption("IPO", "Raise $100M but lose 30% of final NPV", 100, "Only in Round 4 or 5", "30% NPV penalty")
        ]

    def create_events(self):
        """Create event cards"""
        self.events = [
            Event("Economic Downturn", "Economic downturn affects revenue", "−15% revenue this round"),
            Event("Cybersecurity Breach", "Security breach costs money", "−$15M cash unless secured"),
            Event("Data Leak Scandal", "Data leak affects user trust", "Lose 1M users"),
            Event("Regulatory Fine", "Regulatory issues lead to fine", "−$10M cash if compliance project missing"),
            Event("System Crash", "Major system failure", "Lose 1 turn"),
            Event("Market Expansion", "New market opportunity", "Gain 0.5M users"),
            Event("Strategic Partnership", "New partnership opportunity", "Gain $10M cash"),
            Event("Talent Acquisition", "Key talent joins company", "Next project costs 10% less")
        ]

    def create_board(self):
        """Create game board with 20 tiles"""
        # Create a balanced board with different tile types
        tile_types = {
            "Investment": 8,
            "Financing": 2,
            "Event": 4,
            "Neutral": 4,
            "Special": 2
        }

        # Create a list of positions for each tile type
        positions = list(range(20))
        random.shuffle(positions)

        # Assign tile types to positions
        investment_positions = positions[:tile_types["Investment"]]
        financing_positions = positions[tile_types["Investment"]:tile_types["Investment"]+tile_types["Financing"]]
        event_positions = positions[tile_types["Investment"]+tile_types["Financing"]:tile_types["Investment"]+tile_types["Financing"]+tile_types["Event"]]
        neutral_positions = positions[tile_types["Investment"]+tile_types["Financing"]+tile_types["Event"]:tile_types["Investment"]+tile_types["Financing"]+tile_types["Event"]+tile_types["Neutral"]]
        special_positions = positions[tile_types["Investment"]+tile_types["Financing"]+tile_types["Event"]+tile_types["Neutral"]:]

        # Create board with 20 tiles
        self.board = [None] * 20

        # Assign Investment tiles
        for i, pos in enumerate(investment_positions):
            project = self.projects[i % len(self.projects)]
            self.board[pos] = Tile(pos, f"Investment: {project.name}", "Investment", project)

        # Assign Financing tiles
        for i, pos in enumerate(financing_positions):
            self.board[pos] = Tile(pos, "Financing Opportunity", "Financing")

        # Assign Event tiles
        for i, pos in enumerate(event_positions):
            self.board[pos] = Tile(pos, "Market Event", "Event")

        # Assign Neutral tiles
        for i, pos in enumerate(neutral_positions):
            self.board[pos] = Tile(pos, "Revenue Collection", "Neutral")

        # Assign Special tiles
        self.board[special_positions[0]] = Tile(special_positions[0], "IPO Opportunity", "Special", "IPO")
        self.board[special_positions[1]] = Tile(special_positions[1], "Strategic Decision", "Special", "Strategy")

    def add_player(self, name):
        """Add a player to the game"""
        player = Player(name)
        self.players.append(player)

    def roll_dice(self):
        """Roll a dice (1-6)"""
        return random.randint(1, 6)

    def move_player(self, player, steps):
        """Move player on the board"""
        player.position = (player.position + steps) % len(self.board)
        return self.board[player.position]

    def handle_investment_tile(self, player, tile):
        """Handle landing on an investment tile"""
        project = tile.action

        if project.owner is not None:
            print(f"This project is already owned by {project.owner.name}")
            return

        print(f"\nInvestment Opportunity: {project.name}")
        print(f"Cost: ${project.cost}M")
        print(f"Annual Cash Flow: ${project.annual_cash_flow}M for {project.life} years")
        print(f"Risk Level: {project.risk_level}")
        print(f"User Gain: {project.user_gain}M users")
        print(f"NPV: ${project.calculate_npv():.2f}M")
        print(f"IRR: {project.calculate_irr()*100:.2f}%")
        print(f"Payback Period: {project.calculate_payback_period():.2f} years")

        if not player.can_afford(project.cost):
            print(f"You cannot afford this project (Cash: ${player.cash}M)")
            return

        choice = input(f"\nDo you want to invest in {project.name} for ${project.cost}M? (y/n): ").lower()
        if choice == 'y':
            if player.pay(project.cost):
                player.add_project(project, self.current_round)
                player.add_users(project.user_gain)
                print(f"\nYou have successfully invested in {project.name}!")
                print(f"You gained {project.user_gain}M users!")
            else:
                print("Transaction failed. Insufficient funds.")
        else:
            print("You decided not to invest in this project.")

    def handle_financing_tile(self, player, tile):
        """Handle landing on a financing tile"""
        print("\nFinancing Opportunity")
        print("Available options:")

        available_options = []

        for i, option in enumerate(self.financing_options):
            # Check conditions
            if option.name == "VC Funding" and player.vc_funding_used:
                continue  # Skip if VC funding already used
            if option.name == "IPO" and self.current_round < 4:
                continue  # Skip if not in round 4 or 5

            available_options.append(option)
            print(f"{i+1}. {option.name}: {option.description} ({option.conditions})")

        if not available_options:
            print("No financing options available at this time.")
            return

        try:
            choice = int(input("\nChoose a financing option (0 to skip): "))
            if choice == 0:
                print("You decided not to take any financing.")
                return

            if 1 <= choice <= len(available_options):
                selected_option = available_options[choice-1]

                if selected_option.name == "Debt":
                    amount = min(int(input(f"How much debt do you want to take? (max ${selected_option.max_amount}M): ")), selected_option.max_amount)
                    player.receive(amount)
                    player.add_financing(selected_option, amount)
                    print(f"You took ${amount}M in debt at 6% annual interest.")

                elif selected_option.name == "VC Funding":
                    player.receive(selected_option.max_amount)
                    player.add_financing(selected_option, selected_option.max_amount)
                    print(f"You received ${selected_option.max_amount}M in VC funding, but lost 10% of your NPV.")

                elif selected_option.name == "Equity":
                    amount = min(int(input(f"How much equity financing do you want to raise? (max ${selected_option.max_amount}M): ")), selected_option.max_amount)
                    player.receive(amount)
                    player.add_financing(selected_option, amount)
                    print(f"You raised ${amount}M through equity, but diluted your NPV by 20%.")

                elif selected_option.name == "IPO":
                    player.receive(selected_option.max_amount)
                    player.add_financing(selected_option, selected_option.max_amount)
                    print(f"You conducted an IPO and raised ${selected_option.max_amount}M, but your final NPV will be reduced by 30%.")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a valid number.")

    def handle_event_tile(self, player, tile):
        """Handle landing on an event tile"""
        event = random.choice(self.events)
        print(f"\nEvent: {event.name}")
        print(f"Description: {event.description}")
        print(f"Impact: {event.impact}")

        # Apply event effects
        if event.name == "Economic Downturn":
            # 15% revenue reduction this round
            revenue_reduction = sum(p.annual_cash_flow for p in player.projects) * 0.15
            player.cash -= revenue_reduction
            print(f"You lost ${revenue_reduction:.2f}M in revenue due to the economic downturn.")

        elif event.name == "Cybersecurity Breach":
            # $15M cash loss unless secured
            has_security = any(p.name == "AI Fraud Prevention" or p.name == "Blockchain Integration" for p in player.projects)
            if has_security:
                print("Your security investments protected you from the breach!")
            else:
                player.cash -= 15
                print("You lost $15M due to the cybersecurity breach.")

        elif event.name == "Data Leak Scandal":
            # Lose 1M users
            player.lose_users(1)
            print("You lost 1M users due to the data leak scandal.")

        elif event.name == "Regulatory Fine":
            # $10M fine if compliance project missing
            has_compliance = any(p.name == "AI Fraud Prevention" for p in player.projects)
            if has_compliance:
                print("Your compliance investments protected you from the fine!")
            else:
                player.cash -= 10
                print("You were fined $10M due to regulatory issues.")

        elif event.name == "System Crash":
            # Skip next turn
            player.skip_next_turn = True
            print("You will skip your next turn due to the system crash.")

        elif event.name == "Market Expansion":
            # Gain 0.5M users
            player.add_users(0.5)
            print("You gained 0.5M users due to market expansion.")

        elif event.name == "Strategic Partnership":
            # Gain $10M
            player.receive(10)
            print("You gained $10M from a strategic partnership.")

        elif event.name == "Talent Acquisition":
            # Next project costs 10% less
            print("Your next project will cost 10% less due to talent acquisition.")
            # This will be handled when the player buys their next project

    def handle_neutral_tile(self, player, tile):
        """Handle landing on a neutral tile"""
        print("\nRevenue Collection")
        revenue = player.collect_project_revenues()
        print(f"You collected ${revenue}M in revenue from your projects.")

    def handle_special_tile(self, player, tile):
        """Handle landing on a special tile"""
        if tile.action == "IPO":
            if self.current_round >= 4 and not player.ipo_done:
                choice = input("\nDo you want to conduct an IPO? This will raise $100M but reduce your final NPV by 30%. (y/n): ").lower()
                if choice == 'y':
                    player.receive(100)
                    player.ipo_done = True
                    print("You successfully conducted an IPO and raised $100M!")
                else:
                    print("You decided not to conduct an IPO at this time.")
            else:
                print("\nIPO is only available in rounds 4 and 5, and only once per game.")

        elif tile.action == "Strategy":
            print("\nStrategic Decision Point")
            if not player.projects:
                print("You don't have any projects to make strategic decisions about.")
                return

            print("Your projects:")
            for i, project in enumerate(player.projects):
                print(f"{i+1}. {project.name}")

            try:
                project_choice = int(input("\nChoose a project to make a strategic decision about (0 to skip): "))
                if project_choice == 0:
                    print("You decided not to make any strategic decisions.")
                    return

                if 1 <= project_choice <= len(player.projects):
                    selected_project = player.projects[project_choice-1]

                    print("\nStrategic options:")
                    print("1. Expand (Increase annual cash flow by 50% for $20M)")
                    print("2. Pivot (Change project focus for $15M)")
                    print("3. Sell (Recover 50% of initial investment)")

                    strategy_choice = int(input("\nChoose a strategic option (0 to skip): "))

                    if strategy_choice == 1:  # Expand
                        if player.can_afford(20):
                            player.pay(20)
                            selected_project.annual_cash_flow *= 1.5
                            print(f"You expanded {selected_project.name}! Annual cash flow increased to ${selected_project.annual_cash_flow}M.")
                        else:
                            print("You cannot afford this expansion.")

                    elif strategy_choice == 2:  # Pivot
                        if player.can_afford(15):
                            player.pay(15)
                            selected_project.annual_cash_flow *= 1.2
                            selected_project.life += 1
                            print(f"You pivoted {selected_project.name}! Annual cash flow increased to ${selected_project.annual_cash_flow}M and life extended by 1 year.")
                        else:
                            print("You cannot afford this pivot.")

                    elif strategy_choice == 3:  # Sell
                        recovery = selected_project.cost * 0.5
                        player.receive(recovery)
                        player.projects.remove(selected_project)
                        selected_project.owner = None
                        print(f"You sold {selected_project.name} and recovered ${recovery}M.")

                    else:
                        print("Invalid choice or you decided to skip.")
                else:
                    print("Invalid project choice.")
            except ValueError:
                print("Please enter a valid number.")

    def handle_end_of_round(self):
        """Handle end of round activities"""
        print("\n" + "="*50)
        print(f"End of Round {self.current_round}")
        print("="*50)

        # Apply maintenance costs and debt interest
        for player in self.players:
            # Pay debt interest
            if player.debt > 0:
                interest = player.debt * 0.06
                if player.can_afford(interest):
                    player.cash -= interest
                    print(f"{player.name} paid ${interest}M in debt interest.")
                else:
                    # If player can't pay interest, they lose the game
                    print(f"{player.name} couldn't pay ${interest}M in debt interest and is bankrupt!")
                    self.players.remove(player)

        # Show scoreboard
        self.show_scoreboard()

        # Increment round
        self.current_round += 1

        if self.current_round > 5:
            self.game_over = True
            self.end_game()
        else:
            print(f"\nStarting Round {self.current_round}...")
            time.sleep(2)

    def show_scoreboard(self):
        """Show the current scoreboard"""
        print("\nCurrent Standings:")

        headers = ["Player", "Cash ($M)", "Users (M)", "Projects", "NPV ($M)", "Debt ($M)"]
        table_data = []

        for player in self.players:
            npv = player.calculate_total_npv(self.current_round)
            projects_count = len(player.projects)
            table_data.append([
                player.name,
                f"{player.cash:.2f}",
                f"{player.users:.2f}",
                projects_count,
                f"{npv:.2f}",
                f"{player.debt:.2f}"
            ])

        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    def end_game(self):
        """End the game and determine the winner"""
        print("\n" + "="*50)
        print("GAME OVER")
        print("="*50)

        # Calculate final scores
        final_scores = []

        for player in self.players:
            npv = player.calculate_total_npv(self.current_round)
            npv_score = npv * 0.4  # 40% weight
            users_score = player.users * 0.3  # 30% weight
            cash_score = player.cash * 0.1  # 10% weight

            # Bonus for strategic moves (20% weight)
            strategic_score = 0
            if player.ipo_done:
                strategic_score += 10
            strategic_score += len(player.projects) * 2
            strategic_score *= 0.2  # 20% weight

            total_score = npv_score + users_score + cash_score + strategic_score

            final_scores.append((player, total_score, npv, player.users, player.cash, strategic_score))

        # Sort by total score
        final_scores.sort(key=lambda x: x[1], reverse=True)

        # Display final results
        print("\nFinal Results:")

        headers = ["Rank", "Player", "Total Score", "NPV ($M)", "Users (M)", "Cash ($M)", "Strategic"]
        table_data = []

        for i, (player, score, npv, users, cash, strategic) in enumerate(final_scores):
            table_data.append([
                i+1,
                player.name,
                f"{score:.2f}",
                f"{npv:.2f}",
                f"{users:.2f}",
                f"{cash:.2f}",
                f"{strategic:.2f}"
            ])

        print(tabulate(table_data, headers=headers, tablefmt="grid"))

        # Announce winner
        winner = final_scores[0][0]
        print(f"\nCongratulations, {winner.name}! You are the most successful CFO with a score of {final_scores[0][1]:.2f}!")

    def play_turn(self, player):
        """Play a single turn for a player"""
        if player.skip_next_turn:
            print(f"\n{player.name}'s turn is skipped due to system crash.")
            player.skip_next_turn = False
            return

        print("\n" + "="*50)
        print(f"{player.name}'s Turn (Round {self.current_round})")
        print("="*50)
        print(f"Current Position: {player.position}")
        print(f"Cash: ${player.cash}M")
        print(f"Users: {player.users}M")
        print(f"Projects: {len(player.projects)}")

        input("\nPress Enter to roll the dice...")

        dice_roll = self.roll_dice()
        print(f"\nYou rolled a {dice_roll}!")

        # Move player
        tile = self.move_player(player, dice_roll)
        print(f"You landed on: {tile.name} (Position {tile.position})")

        # Handle tile action
        if tile.tile_type == "Investment":
            self.handle_investment_tile(player, tile)
        elif tile.tile_type == "Financing":
            self.handle_financing_tile(player, tile)
        elif tile.tile_type == "Event":
            self.handle_event_tile(player, tile)
        elif tile.tile_type == "Neutral":
            self.handle_neutral_tile(player, tile)
        elif tile.tile_type == "Special":
            self.handle_special_tile(player, tile)

    def play_game(self):
        """Main game loop"""
        # Get number of players
        num_players = int(input("Enter number of players (3-5): "))
        while num_players < 3 or num_players > 5:
            num_players = int(input("Please enter a valid number of players (3-5): "))

        # Get player names
        for i in range(num_players):
            name = input(f"Enter name for Player {i+1}: ")
            self.add_player(name)

        print("\nStarting Finopoly Game!")
        print("Each player starts with $100M and 1M users.")
        print("The goal is to maximize your company value over 5 rounds.")

        # Main game loop
        while not self.game_over:
            # Play a round
            for i in range(len(self.players)):
                self.current_player_index = i
                self.play_turn(self.players[i])

                # Check if game is over
                if self.game_over:
                    break

                # Pause between turns
                if i < len(self.players) - 1:
                    input("\nPress Enter for next player's turn...")

            # End of round
            if not self.game_over:
                self.handle_end_of_round()

# Run the game
if __name__ == "__main__":
    try:
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')

        print
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')

        print("""
╔═══════════════════════════════════════════════════════════════╗
║                         FINOPOLY                              ║
║           The Financial Management Simulation Game            ║
╚═══════════════════════════════════════════════════════════════╝
""")

        game = Finopoly()
        game.play_game()
    except Exception as e:
        print(f"An error occurred: {e}")
