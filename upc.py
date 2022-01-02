#!/usr/bin/env python-mr
#
# See https://en.wikipedia.org/wiki/Universal_Product_Code
#

from collections import defaultdict
from enum import Enum, auto

class UpcType(Enum):
  Normal = auto()
  VariableWeight = auto()
  Drugs = auto()
  Local = auto()
  Coupon = auto()

  @staticmethod
  def lookup(digit):
    if digit % 10 != digit:
      raise Exception("Can not lookup UPC type for numbers outside of 0 to 9: " + str(digit))

    if digit == 2:
      return UpcType.VariableWeight
    elif digit == 3:
      return UpcType.Drugs
    elif digit == 4:
      return UpcType.Local
    elif digit == 5:
      return UpcType.Coupon

    return UpcType.Normal


class Upc:
  BASE = 10 ** 6

  @staticmethod
  def decode(digits):
    if digits < Upc.BASE * 2: # short code
      raise Exception("Can not handle UPC-E codes without barcode parity information")
    else:
      l, r = divmod(digits, Upc.BASE)
      return Upc(l, r)

  def encode(self):
    return self.left * Upc.BASE + self.right

  def __init__(self, left, right):
    self.left = left
    self.right = right
    self._checksums = None

  def __repr__(self):
    return f"Upc({self.left}, {self.right})"

  def _check_digit(self):
    return self.right % 10

  def _lead_digit(self):
    return self.left // (Upc.BASE // 10)

  def type(self):
    return UpcType.lookup(self._lead_digit())

  def check(self) -> bool:
    "Returns true if the UPC checksum is correct"
    if self._checksums is None:
      digits = []
      d = self.left * Upc.BASE + self.right
      for i in range(12):
        digits.append(d % 10)
        d = d // 10
      digits.reverse()

      check = sum(digits[::2]) * 3 + sum(digits[1::2])

      self._checksums = (check % 10) == 0

    return self._checksums

