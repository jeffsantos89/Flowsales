import unittest
import numpy as np
from src.security.ai_adversarial_attack import AdversarialAttack
import time

class TestAdversarialAttack(unittest.TestCase):

    def setUp(self):
        self.attack = AdversarialAttack()
        self.sample_input = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        self.sample_label = np.array([1, 0])
        self.epsilon = 0.01

    def test_generate_adversarial_example(self):
        adversarial_example = self.attack.generate(self.sample_input, self.sample_label, self.epsilon)
        self.assertEqual(adversarial_example.shape, self.sample_input.shape)
        self.assertFalse(np.array_equal(adversarial_example, self.sample_input))

    def test_adversarial_example_within_epsilon(self):
        adversarial_example = self.attack.generate(self.sample_input, self.sample_label, self.epsilon)
        perturbation = np.abs(adversarial_example - self.sample_input)
        self.assertTrue(np.all(perturbation <= self.epsilon))

    def test_attack_success_rate(self):
        success_rate = self.attack.evaluate(self.sample_input, self.sample_label, self.epsilon)
        self.assertGreaterEqual(success_rate, 0)
        self.assertLessEqual(success_rate, 1)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            self.attack.generate(None, self.sample_label, self.epsilon)
        with self.assertRaises(ValueError):
            self.attack.generate(self.sample_input, None, self.epsilon)
        with self.assertRaises(ValueError):
            self.attack.generate(self.sample_input, self.sample_label, -0.01)

    def test_performance(self):
        start_time = time.time()
        self.attack.generate(self.sample_input, self.sample_label, self.epsilon)
        duration = time.time() - start_time
        self.assertLess(duration, 1, "Adversarial attack generation took too long")

if __name__ == '__main__':
    unittest.main()