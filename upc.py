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


# This handles EAN-13 codes...sort of.
# Only because they mostly look like UPC-A.
class Upc:
  BASE = 10 ** 6
  MAX_UPC = 10 ** 12 - 1
  MAX_EAN = 10 ** 13 - 1

  @staticmethod
  def decode(digits):
    if digits < Upc.BASE * 2: # short code
      raise Exception("Can not handle UPC-E codes without barcode parity information")
    else:
      l, r = divmod(digits, Upc.BASE)
      return Upc(l, r)

  @staticmethod
  def __checksum(d):
      length = 12
      if d > Upc.MAX_UPC:
        # ie, it is EAN-13.
        length = 13

      digits = []
      for i in range(length):
        digits.append(d % 10)
        d = d // 10
      digits.reverse()

      return (sum(digits[::2]) * 3 + sum(digits[1::2])) % 10

  def encode(self, canonical=False):
    # Return what was passed in by default.
    if not canonical or self.type() != UpcType.VariableWeight:
      return self.left * Upc.BASE + self.right

    # Otherwise, only for VariableType, zero out the
    # bottom bits & compute new valid checksum.
    check = Upc.__checksum(self.left * Upc.BASE)

    # Checksum digit changes weight (1 or 3) depending on the code length.
    if self.left * Upc.BASE <= Upc.MAX_UPC:
      return self.left * Upc.BASE + check

    return self.left * Upc.BASE + ((check * 3) % 10)
    

  def __init__(self, left, right):
    self.left = left
    self.right = right
    self._checksums = None

  def __repr__(self):
    return f"Upc({self.left}, {self.right})"

  def _check_digit(self):
    return self.right % 10

  def _lead_digit(self):
    # This is probably not correct for EAN-13...
    firstish = self.left // (Upc.BASE // 10)
    if firstish < 10:
      return firstish
    return firstish // 10

  def type(self):
    return UpcType.lookup(self._lead_digit())

  def check(self) -> bool:
    "Returns true if the UPC checksum is correct"
    if self._checksums is None:
      check = Upc.__checksum(self.left * Upc.BASE + self.right)
      self._checksums = check == 0

    return self._checksums

