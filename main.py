import secrets
from typing import List, Dict, Any

if __name__ == "__main__":
    # pp_utils.process_all_dictionaries(4, 9)

    def secure_shuffle(lst: List[int]) -> None:
        """
        Perform an in-place Fisher–Yates shuffle using secrets.randbelow for cryptographic security.
        
        :param lst: List of integers to shuffle in place.
        """
        for i in range(len(lst) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            lst[i], lst[j] = lst[j], lst[i]

    def create_jit_partition(n: int, minw: int, maxw: int) -> List[int]:
        """
        Generate one random integer partition of `n` into parts between minw and maxw (inclusive),
        using a dynamic valid-picks approach with the secrets module for secure randomness.
        The result is shuffled for extra entropy.

        :param n: Total sum to partition.
        :param minw: Minimum allowed part size.
        :param maxw: Maximum allowed part size.
        :return: A list of integers summing to n, each in [minw, maxw].
        :raises ValueError: If bounds are invalid or if no partition is possible.
        """
        if minw > maxw:
            raise ValueError(f"Invalid bounds: minw ({minw}) > maxw ({maxw})")
        if n < minw:
            raise ValueError(f"No partition possible: n ({n}) < minw ({minw})")

        R = n
        parts: List[int] = []

        # Continue until the remainder R is zero
        while R > 0:
            # Compute the count of picks in [minw..max_pick]
            max_pick = min(maxw, R - minw)
            picks_count = max_pick - minw + 1 if max_pick >= minw else 0
            # Allow finishing with R itself if R <= maxw
            allow_finish = 1 if R <= maxw else 0
            total_options = picks_count + allow_finish

            if total_options <= 0:
                raise ValueError(f"No valid picks for R={R} with minw={minw}, maxw={maxw}")

            # Select a random index among all valid options
            idx = secrets.randbelow(total_options)
            if idx < picks_count:
                w = minw + idx
            else:
                w = R

            parts.append(w)
            R -= w

        # Shuffle for extra entropy
        secure_shuffle(parts)
        return parts

    def test_jit_partition_creation(n: int, minw: int, maxw: int, repetitions: int) -> Dict[str, Any]:
      """
      Test create_jit_partition by generating 'repetitions' partitions for given parameters.
      Checks that each partition sums to n and each part is within [minw, maxw].
      Returns a summary dictionary with:
        - 'total': total attempts,
        - 'errors': number of failed validations,
        - 'distribution': mapping of part_count -> frequency.
      """
      print(f'n={n}, minw={minw}, maxw={maxw}, repetitions={repetitions}')
      errors = 0
      distribution: Dict[int, int] = {}
      
      for i in range(repetitions):
          try:
              parts = create_jit_partition(n, minw, maxw)
              print(parts)
              # Validation: sum and bounds
              assert sum(parts) == n, f"Sum {sum(parts)} != {n}"
              assert all(minw <= w <= maxw for w in parts), f"Parts out of bounds: {parts}"
              count = len(parts)
              distribution[count] = distribution.get(count, 0) + 1
          except AssertionError as ae:
              errors += 1
              print(f"Assertion error on iteration {i}: {ae}")
          except Exception as e:
              errors += 1
              print(f"Unexpected error on iteration {i}: {e}")
      
      summary = {
          "total": repetitions,
          "errors": errors,
          "distribution": distribution
      }
      return summary

    # Example usage (uncomment to run):
    result = test_jit_partition_creation(n=20, minw=4, maxw=9, repetitions=20)
    print(result)
