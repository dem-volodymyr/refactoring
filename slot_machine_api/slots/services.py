import random
from decimal import Decimal


class ReelService:
    def __init__(self, symbols):
        self.symbols = symbols

    def generate_spin(self, num_reels=5, visible_rows=3):
        """Generate a random spin result with 5 reels and 3 visible symbols per reel."""
        result = {}
        for reel in range(num_reels):
            # Select random symbols for this reel
            shuffled_symbols = random.sample(list(self.symbols), len(self.symbols))
            result[reel] = [shuffled_symbols[i].name for i in range(visible_rows)]
        return result

    @staticmethod
    def flip_horizontal(result):
        """Convert vertical reels to horizontal rows for win checking."""
        horizontal_values = []
        for value in result.values():
            horizontal_values.append(value)

        rows, cols = len(horizontal_values), len(horizontal_values[0])
        hvals2 = [[""] * rows for _ in range(cols)]

        for x in range(rows):
            for y in range(cols):
                hvals2[y][rows - x - 1] = horizontal_values[x][y]

        hvals3 = [item[::-1] for item in hvals2]
        return hvals3

    @staticmethod
    def longest_seq(hit):
        """Find the longest sequence of consecutive indices."""
        sub_seq_length, longest = 1, 1
        start, end = 0, 0

        for i in range(len(hit) - 1):
            if hit[i] == hit[i + 1] - 1:
                sub_seq_length += 1
                if sub_seq_length > longest:
                    longest = sub_seq_length
                    start = i + 2 - sub_seq_length
                    end = i + 2
            else:
                sub_seq_length = 1

        return hit[start:end]

    def check_wins(self, result):
        """Check for winning combinations in the spin result."""
        hits = {}
        horizontal = self.flip_horizontal(result)

        for row in horizontal:
            for sym in row:
                if row.count(sym) > 2:  # Potential win
                    possible_win = [idx for idx, val in enumerate(row) if sym == val]

                    # Check possible_win for a subsequence longer than 2 and add to hits
                    longest = self.longest_seq(possible_win)
                    if len(longest) > 2:
                        hits[horizontal.index(row) + 1] = [sym, longest]

        return hits if hits else None

    def calculate_payout(self, win_data, bet_size):
        """Calculate payout based on win data and bet size."""
        if not win_data:
            return Decimal('0.00')

        from .models import Symbol
        total_payout = Decimal('0.00')

        for row_number, win_info in win_data.items():
            sym_name, indices = win_info
            symbol = Symbol.objects.get(name=sym_name)
            combo_length = len(indices)
            total_payout += Decimal(bet_size) * combo_length * symbol.payout_multiplier

        return total_payout


class SlotMachineService:
    def __init__(self):
        from .models import Symbol
        symbols = Symbol.objects.all()
        self.reel_service = ReelService(symbols)

    def play_spin(self, player, bet_size):
        """Process a single spin of the slot machine."""
        # Check if player has enough balance
        if player.balance < Decimal(bet_size):
            return {
                'success': False,
                'message': 'Insufficient balance'
            }

        # Update player balance
        player.balance -= Decimal(bet_size)
        player.total_wager += Decimal(bet_size)
        player.save()

        # Generate spin result
        result = self.reel_service.generate_spin()

        # Check for wins
        win_data = self.reel_service.check_wins(result)
        payout = Decimal('0.00')

        # Calculate and process payout if there's a win
        if win_data:
            payout = self.reel_service.calculate_payout(win_data, bet_size)
            player.balance += payout
            player.total_won += payout
            player.save()

        # Create and return the spin record
        from .models import Spin, Game
        game, _ = Game.objects.get_or_create(player=player)

        spin = Spin.objects.create(
            game=game,
            bet_amount=bet_size,
            payout=payout,
            result=result,
            win_data=win_data
        )

        return {
            'success': True,
            'spin_id': spin.id,
            'result': result,
            'win_data': win_data,
            'payout': payout,
            'current_balance': player.balance
        }
