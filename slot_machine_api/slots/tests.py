from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from .models import Player, Symbol, Game, Spin
from .services import SlotMachineService, ReelService

class SlotMachineTests(TestCase):
    def setUp(self):
        """Set up test user, player, and at least 3 symbols for all tests."""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user, balance=Decimal('1000.00'))
        self.symbol1 = Symbol.objects.create(name='Cherry', image_path='cherry.png', payout_multiplier=Decimal('2.5'))
        self.symbol2 = Symbol.objects.create(name='Lemon', image_path='lemon.png', payout_multiplier=Decimal('1.5'))
        self.symbol3 = Symbol.objects.create(name='Diamond', image_path='diamond.png', payout_multiplier=Decimal('3.0'))
        self.client = APIClient()

    def test_registration_api(self):
        """Test user registration endpoint."""
        response = self.client.post('/api/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('balance', response.data)

    def test_player_info_api(self):
        """Test player info endpoint."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/players/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_symbol_str(self):
        """Test string representation of Symbol."""
        self.assertEqual(str(self.symbol1), 'Cherry')

    def test_game_str(self):
        """Test string representation of Game."""
        game = Game.objects.create(player=self.player)
        self.assertIn('Game', str(game))

    def test_spin_str(self):
        """Test string representation of Spin."""
        game = Game.objects.create(player=self.player)
        spin = Spin.objects.create(game=game, bet_amount=Decimal('10.00'), payout=Decimal('0.00'), result={})
        self.assertIn('Spin', str(spin))

    def test_slot_machine_service_insufficient_balance(self):
        """Test play_spin returns error if player has insufficient balance."""
        self.player.balance = Decimal('0.00')
        self.player.save()
        service = SlotMachineService()
        result = service.play_spin(self.player, Decimal('10.00'))
        self.assertFalse(result['success'])
        self.assertIn('Insufficient balance', result['message'])

    def test_slot_machine_service_successful_spin(self):
        """Test play_spin updates player balance correctly on success."""
        start_balance = self.player.balance
        service = SlotMachineService()
        result = service.play_spin(self.player, Decimal('10.00'))
        self.assertTrue(result['success'])
        self.player.refresh_from_db()
        expected_balance = start_balance - Decimal('10.00') + result['payout']
        self.assertEqual(self.player.balance, expected_balance)

    def test_reel_service_generate_spin(self):
        """Test generate_spin returns correct shape with enough symbols."""
        symbols = Symbol.objects.all()
        reel_service = ReelService(symbols)
        result = reel_service.generate_spin()
        self.assertEqual(len(result), 5)  # 5 reels
        for reel in result.values():
            self.assertEqual(len(reel), 3)  # 3 visible rows

    def test_reel_service_check_wins(self):
        """Test check_wins detects a winning row."""
        symbols = Symbol.objects.all()
        reel_service = ReelService(symbols)
        # Create a winning row: all 'Cherry'
        result = {i: ['Cherry', 'Cherry', 'Cherry'] for i in range(5)}
        win_data = reel_service.check_wins(result)
        self.assertIsNotNone(win_data)
        self.assertTrue(any('Cherry' in win for win in win_data.values()))

    def test_spin_api_and_balance_update(self):
        """Test spin endpoint returns expected structure and updates balance."""
        self.client.force_authenticate(user=self.user)
        start_balance = self.player.balance
        response = self.client.post('/api/spins/spin/', {'bet_size': '10.00'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.player.refresh_from_db()
        expected_balance = start_balance - Decimal('10.00') + Decimal(str(response.data['payout']))
        self.assertEqual(self.player.balance, expected_balance)
