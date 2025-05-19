import random
from decimal import Decimal

# --- Константи для слот-машини ---
DEFAULT_NUM_REELS = 5
DEFAULT_VISIBLE_ROWS = 3
MIN_WIN_COUNT = 3
INITIAL_PLAYER_BALANCE = Decimal('1000.00')
INITIAL_MACHINE_BALANCE = Decimal('10000.00')
ZERO_DECIMAL = Decimal('0.00')

class ReelService:
    def __init__(self, symbols):
        self.symbols = symbols

    def generate_spin(self, num_reels=DEFAULT_NUM_REELS, visible_rows=DEFAULT_VISIBLE_ROWS):
        """Generate a random spin result with num_reels and visible_rows per reel."""
        result = {}
        for reel in range(num_reels):
            shuffled_symbols = random.sample(list(self.symbols), len(self.symbols))
            result[reel] = [shuffled_symbols[i].name for i in range(visible_rows)]
        return result

    @staticmethod
    def flip_horizontal(result):
        """Convert vertical reels to horizontal rows for win checking."""
        horizontal_values = list(result.values())
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

    def _row_wins(self, row):
        """Check a single row for winning symbols."""
        wins = []
        checked = set()
        for sym in row:
            if sym in checked:
                continue
            checked.add(sym)
            if row.count(sym) >= MIN_WIN_COUNT:
                possible_win = [idx for idx, val in enumerate(row) if sym == val]
                longest = self.longest_seq(possible_win)
                if len(longest) >= MIN_WIN_COUNT:
                    wins.append((sym, longest))
        return wins

    def check_wins(self, result):
        """Check for winning combinations in the spin result."""
        hits = {}
        horizontal = self.flip_horizontal(result)
        for idx, row in enumerate(horizontal):
            row_wins = self._row_wins(row)
            if row_wins:
                hits[idx + 1] = row_wins[0]  # Підтримка лише першого виграшу на рядок
        return hits if hits else None

    def calculate_payout(self, win_data, bet_size):
        """Calculate payout based on win data and bet size."""
        if not win_data:
            return ZERO_DECIMAL
        from .models import Symbol
        total_payout = ZERO_DECIMAL
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
        if player.balance < Decimal(bet_size):
            return {
                'success': False,
                'message': 'Insufficient balance'
            }
        self._update_player_balance_on_bet(player, bet_size)
        result = self.reel_service.generate_spin()
        win_data = self.reel_service.check_wins(result)
        payout = ZERO_DECIMAL
        if win_data:
            payout = self.reel_service.calculate_payout(win_data, bet_size)
            self._update_player_balance_on_win(player, payout)
        spin = self._create_spin_record(player, bet_size, payout, result, win_data)
        return {
            'success': True,
            'spin_id': spin.id,
            'result': result,
            'win_data': win_data,
            'payout': payout,
            'current_balance': player.balance
        }

    def _update_player_balance_on_bet(self, player, bet_size):
        player.balance -= Decimal(bet_size)
        player.total_wager += Decimal(bet_size)
        player.save()

    def _update_player_balance_on_win(self, player, payout):
        player.balance += payout
        player.total_won += payout
        player.save()

    def _create_spin_record(self, player, bet_size, payout, result, win_data):
        from .models import Spin, Game
        game, _ = Game.objects.get_or_create(player=player)
        return Spin.objects.create(
            game=game,
            bet_amount=bet_size,
            payout=payout,
            result=result,
            win_data=win_data
        )
