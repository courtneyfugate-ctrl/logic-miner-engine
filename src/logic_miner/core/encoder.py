import math

class PadicEncoder:
    def __init__(self, p_base):
        """
        Initializes the encoder with a prime base p.
        p must be >= the number of choices per question.
        """
        if not self._is_prime(p_base):
            raise ValueError(f"Base {p_base} must be prime.")
        self.p = p_base

    def _is_prime(self, n):
        if n < 2: return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0: return False
        return True

    def encode(self, responses):
        """
        Maps a list of integer choices [r_0, r_1, ...] to a p-adic integer.
        x = sum(r_i * p^i)
        """
        value = 0
        for i, r in enumerate(responses):
            if r >= self.p:
                raise ValueError(f"Response {r} exceeds base {self.p}")
            value += r * (self.p ** i)
        return value

    def decode(self, value, length):
        """
        Reconstructs the sequence of choices from an integer value.
        """
        responses = []
        for _ in range(length):
            responses.append(value % self.p)
            value //= self.p
        return responses

    def valuation(self, n):
        """Computes v_p(n): the exponent of the highest power of p dividing n."""
        if n == 0: return float('inf')
        v = 0
        while n % self.p == 0:
            v += 1
            n //= self.p
        return v

    def distance(self, val1, val2):
        """Computes ultrametric distance p^(-v_p(val1 - val2))."""
        diff = abs(val1 - val2)
        if diff == 0: return 0.0
        return self.p ** (-self.valuation(diff))
