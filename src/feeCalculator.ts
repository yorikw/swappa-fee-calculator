import {Constants} from "./constants";

export class FeeDeductions {
    ask_price: number;
    shipping_cost: number;
    sales_tax: number;
    featured: boolean;

    listing_price: number;
    buyer_paid: number;
    buyer_fee: number;
    seller_fee: number;
    paypal_fee: number;

    constructor(ask_price: number, shipping_cost = 0.0, sales_tax = 0.0, featured = false) {
        this.ask_price = ask_price;
        this.shipping_cost = shipping_cost;
        this.sales_tax = sales_tax;
        this.featured = featured;

        this.listing_price = this.ask_price * (1 + Constants.BUYER_FEE_RATE);
        this.buyer_paid = this.listing_price + (this.listing_price * (sales_tax / 100));
        this.buyer_fee = this.listing_price - this.ask_price;
        this.seller_fee = this.ask_price * Constants.SELLER_FEE_RATE;
        this.paypal_fee = this.buyer_paid > 0
            ? this.buyer_paid * Constants.PAYPAL_FEE_RATE + Constants.PAYPAL_FIXED_FEE
            : 0;
    }

    afterPaypal(): number {
        return this.ask_price - this.seller_fee - this.paypal_fee;
    }

    afterShipping(): number {
        return this.afterPaypal() - this.shipping_cost;
    }

    finalRevenue(): number {
        return this.featured ? this.afterShipping() - Constants.FEATURED_LISTING_FEE : this.afterShipping();
    }
}
