import argparse


class Constants:
    BUYER_FEE_RATE = 0.03
    SELLER_FEE_RATE = 0.03
    PAYPAL_FEE_RATE = 0.0349
    PAYPAL_FIXED_FEE = 0.49
    FEATURED_LISTING_FEE = 5.0


def ask_price_from_listing_price(listing_price: float) -> int:
    return round(listing_price / (1 + Constants.BUYER_FEE_RATE))


class SwappaFeeCalculation:
    def __init__(
        self,
        ask_price: float = 0.0,
        shipping_cost: float = 0.0,
        sales_tax_rate: float = 0.0,
        featured: bool = False,
    ):
        self.ask_price = ask_price
        self.shipping_cost = shipping_cost
        self.sales_tax_rate = sales_tax_rate
        self.featured = featured

        self.listing_price = self.ask_price * (1 + Constants.BUYER_FEE_RATE)
        self.sales_tax_amount = self.listing_price * (self.sales_tax_rate / 100)
        self.buyer_paid = self.listing_price + self.sales_tax_amount
        self.buyer_fee = self.listing_price - self.ask_price
        self.seller_fee = self.ask_price * Constants.SELLER_FEE_RATE
        self.paypal_fee = (
            self.buyer_paid * Constants.PAYPAL_FEE_RATE + Constants.PAYPAL_FIXED_FEE
            if self.buyer_paid > 0
            else 0.0
        )
        self.featured_listing_fee = (
            Constants.FEATURED_LISTING_FEE if self.featured else 0.0
        )

        self.swappa_payout = self.ask_price - self.seller_fee
        self.after_paypal = self.swappa_payout - self.paypal_fee
        self.after_shipping = self.after_paypal - self.shipping_cost
        self.final_revenue = self.after_shipping - self.featured_listing_fee
        self.marketplace_payment_fees = (
            self.buyer_fee + self.seller_fee + self.paypal_fee
        )
        self.shipping_and_extras = self.shipping_cost + self.featured_listing_fee
        self.total_fees = self.marketplace_payment_fees + self.shipping_and_extras
        self.total_fees_percent = (
            self.total_fees / self.listing_price * 100
            if self.listing_price > 0
            else 0.0
        )


# Backwards-compatible class name used by the older script.
FeeDeductions = SwappaFeeCalculation


def formatted_output(calc: SwappaFeeCalculation) -> str:
    lines = [
        ("Buyer pays:", f"${calc.buyer_paid:.2f}"),
        (
            "Listing price:",
            f"${calc.listing_price:.2f} (${calc.ask_price:.2f} ask price + ${calc.buyer_fee:.2f} buyer fee)",
        ),
        (
            "Ask price:",
            f"${calc.ask_price:.2f} (-${calc.buyer_fee:.2f} buyer fee @ {Constants.BUYER_FEE_RATE * 100:.2f}%)",
        ),
        (
            "Swappa payout:",
            f"${calc.swappa_payout:.2f} (-${calc.seller_fee:.2f} seller fee @ {Constants.SELLER_FEE_RATE * 100:.2f}%)",
        ),
        (
            "After PayPal:",
            f"${calc.after_paypal:.2f} (-${calc.paypal_fee:.2f} PayPal fee @ {Constants.PAYPAL_FEE_RATE * 100:.2f}% + ${Constants.PAYPAL_FIXED_FEE:.2f})",
        ),
        (
            "After shipping:",
            f"${calc.after_shipping:.2f} (-${calc.shipping_cost:.2f} shipping)",
        ),
        (
            "Final profit:",
            f"${calc.final_revenue:.2f} (-${calc.featured_listing_fee:.2f} featured listing fee)",
        ),
        (
            "Total fees:",
            f"${calc.total_fees:.2f} (${calc.marketplace_payment_fees:.2f} marketplace/payment fees + ${calc.shipping_and_extras:.2f} shipping/extras; {calc.total_fees_percent:.2f}% of listing price)",
        ),
    ]

    max_len = max(len(line[0]) for line in lines)
    return "\n".join(f"{line[0].ljust(max_len)} {line[1]}" for line in lines)


def test_fee_calculator() -> None:
    test_cases = [
        {
            "input": {
                "ask_price": 500,
                "shipping_cost": 15,
                "sales_tax_rate": 8,
                "featured": True,
            },
            "expected": """\
Buyer pays:     $556.20
Listing price:  $515.00 ($500.00 ask price + $15.00 buyer fee)
Ask price:      $500.00 (-$15.00 buyer fee @ 3.00%)
Swappa payout:  $485.00 (-$15.00 seller fee @ 3.00%)
After PayPal:   $465.10 (-$19.90 PayPal fee @ 3.49% + $0.49)
After shipping: $450.10 (-$15.00 shipping)
Final profit:   $445.10 (-$5.00 featured listing fee)
Total fees:     $69.90 ($49.90 marketplace/payment fees + $20.00 shipping/extras; 13.57% of listing price)""",
        },
        {
            "input": {
                "ask_price": ask_price_from_listing_price(515),
                "shipping_cost": 15,
                "sales_tax_rate": 8,
                "featured": True,
            },
            "expected": """\
Buyer pays:     $556.20
Listing price:  $515.00 ($500.00 ask price + $15.00 buyer fee)
Ask price:      $500.00 (-$15.00 buyer fee @ 3.00%)
Swappa payout:  $485.00 (-$15.00 seller fee @ 3.00%)
After PayPal:   $465.10 (-$19.90 PayPal fee @ 3.49% + $0.49)
After shipping: $450.10 (-$15.00 shipping)
Final profit:   $445.10 (-$5.00 featured listing fee)
Total fees:     $69.90 ($49.90 marketplace/payment fees + $20.00 shipping/extras; 13.57% of listing price)""",
        },
        {
            "input": {},
            "expected": """\
Buyer pays:     $0.00
Listing price:  $0.00 ($0.00 ask price + $0.00 buyer fee)
Ask price:      $0.00 (-$0.00 buyer fee @ 3.00%)
Swappa payout:  $0.00 (-$0.00 seller fee @ 3.00%)
After PayPal:   $0.00 (-$0.00 PayPal fee @ 3.49% + $0.49)
After shipping: $0.00 (-$0.00 shipping)
Final profit:   $0.00 (-$0.00 featured listing fee)
Total fees:     $0.00 ($0.00 marketplace/payment fees + $0.00 shipping/extras; 0.00% of listing price)""",
        },
    ]

    for test in test_cases:
        calc = SwappaFeeCalculation(**test["input"])
        result = formatted_output(calc)
        assert result == test["expected"], (
            f"Expected:\n{test['expected']}\nGot:\n{result}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Swappa Fee Calculator")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-a",
        "--ask",
        type=float,
        help="Ask price",
    )
    group.add_argument(
        "-l",
        "--listing",
        type=float,
        help="Listing price",
    )
    parser.add_argument("-s", "--shipping", type=float, default=0.0, help="Shipping cost")
    parser.add_argument("-t", "--tax", type=float, default=0.0, help="Sales tax percentage")
    parser.add_argument(
        "-f",
        "--featured",
        action="store_true",
        help="Apply featured listing fee",
    )
    args = parser.parse_args()

    calc = SwappaFeeCalculation(
        ask_price=ask_price_from_listing_price(args.listing)
        if args.listing is not None
        else args.ask,
        shipping_cost=args.shipping,
        sales_tax_rate=args.tax,
        featured=args.featured,
    )
    print(formatted_output(calc))


if __name__ == "__main__":
    test_fee_calculator()
    main()
