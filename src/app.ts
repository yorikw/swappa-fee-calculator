import {FeeDeductions} from './feeCalculator';
import {Constants} from "./constants";

function numberInput(id: string, fallback = 0): number {
    const input = document.getElementById(id) as HTMLInputElement;
    const parsed = parseFloat(input.value);
    return Number.isFinite(parsed) ? parsed : fallback;
}

function checkboxInput(id: string): boolean {
    return (document.getElementById(id) as HTMLInputElement).checked;
}

function currency(value: number): string {
    return `$${value.toFixed(2)}`;
}

function percent(value: number): string {
    return `${value.toFixed(2)}%`;
}

function share(value: number, total: number): number {
    return total > 0 ? (value / total) * 100 : 0;
}

function setText(id: string, value: string) {
    document.getElementById(id)!.innerText = value;
}

function updateOutput() {
    const togglePriceMode = document.getElementById('togglePriceMode') as HTMLInputElement;

    let price = numberInput('priceInput');

    if (togglePriceMode.checked) {
        price = Math.round(price / (1 + Constants.BUYER_FEE_RATE));
    }

    const shippingCost = numberInput('shippingCost');
    const salesTax = numberInput('salesTax');
    const featured = checkboxInput('featured');
    const feeObj = new FeeDeductions(price, shippingCost, salesTax, featured);

    const swappaFees = feeObj.buyer_fee + feeObj.seller_fee + feeObj.paypal_fee;
    const listingExtras = shippingCost + (featured ? Constants.FEATURED_LISTING_FEE : 0);
    const totalFees = swappaFees + listingExtras;
    const finalProfit = feeObj.finalRevenue();
    const profitShare = share(finalProfit, feeObj.listing_price);
    const feesShare = share(totalFees, feeObj.listing_price);

    const positiveProfit = Math.max(0, finalProfit);
    const chartTotal = positiveProfit + swappaFees + listingExtras;
    const profitDegrees = share(positiveProfit, chartTotal) * 3.6;
    const extrasDegrees = share(listingExtras, chartTotal) * 3.6;
    const chart = document.getElementById('profitChart') as HTMLElement;

    chart.style.background = chartTotal > 0
        ? `conic-gradient(var(--profit) 0deg ${profitDegrees}deg, var(--expenses) ${profitDegrees}deg ${profitDegrees + extrasDegrees}deg, var(--fees) ${profitDegrees + extrasDegrees}deg 360deg)`
        : 'conic-gradient(var(--profit) 0deg 360deg)';

    setText('summaryFees', currency(totalFees));
    setText('summaryFeesPercent', `(${percent(feesShare)})`);
    setText('summaryProfit', currency(finalProfit));
    setText('summaryProfitPercent', `(${percent(profitShare)})`);

    setText('buyerPaid', currency(feeObj.buyer_paid));
    setText('buyerPaidDummy',
        `(${currency(feeObj.listing_price)} listing price + ${currency(feeObj.buyer_paid - feeObj.listing_price)} sales tax @ ${percent(salesTax)})`
    );

    setText('listingPrice', currency(feeObj.listing_price));
    setText('listingPriceDiff',
        `(${currency(feeObj.ask_price)} ask price + ${currency(feeObj.buyer_fee)} buyer fee)`
    );

    setText('askPriceOutput', currency(feeObj.ask_price));
    setText('askPriceDiff',
        `(-${currency(feeObj.buyer_fee)} buyer fee @ ${percent(Constants.BUYER_FEE_RATE * 100)})`
    );

    setText('swappaPayout', currency(feeObj.ask_price - feeObj.seller_fee));
    setText('swappaPayoutDiff',
        `(-${currency(feeObj.seller_fee)} seller fee @ ${percent(Constants.SELLER_FEE_RATE * 100)})`
    );

    setText('afterPaypal', currency(feeObj.afterPaypal()));
    setText('afterPaypalDiff',
        feeObj.buyer_paid > 0
            ? `(-${currency(feeObj.paypal_fee)} PayPal fee @ ${percent(Constants.PAYPAL_FEE_RATE * 100)} + ${currency(Constants.PAYPAL_FIXED_FEE)})`
            : `(-${currency(0)} PayPal fee @ ${percent(Constants.PAYPAL_FEE_RATE * 100)} + ${currency(Constants.PAYPAL_FIXED_FEE)})`
    );

    setText('afterShipping', currency(feeObj.afterShipping()));
    setText('afterShippingDiff',
        `(-${currency(shippingCost)} shipping)`
    );

    setText('finalRevenue', currency(finalProfit));
    setText('finalRevenueDiff',
        featured ? `(-${currency(Constants.FEATURED_LISTING_FEE)} featured listing fee)` : `(-${currency(0)} featured listing fee)`
    );

    setText('profitMargin', percent(profitShare));
    setText('netProfit', currency(finalProfit));
    setText('netProfitDiff',
        `(${currency(feeObj.listing_price)} listing price - ${currency(totalFees)} fees/costs)`
    );
    setText('summaryExpenses', currency(listingExtras));
    setText('summarySellingFees', currency(swappaFees));
    setText('totalFees', currency(totalFees));
    setText('totalFeesDiff',
        `(${currency(swappaFees)} marketplace/payment fees + ${currency(listingExtras)} shipping/extras)`
    );
    setText('legendTotalDiff', feeObj.listing_price > 0
        ? `(${percent(totalFees / feeObj.listing_price * 100)} of listing price)`
        : ''
    );
}

function updateInputLabel() {
    const togglePriceMode = document.getElementById('togglePriceMode') as HTMLInputElement;
    const priceLabel = document.getElementById('priceLabel') as HTMLSpanElement;

    priceLabel.innerText = togglePriceMode.checked ? 'Listing Price' : 'Ask Price';
}

function updateAll() {
    updateInputLabel();
    updateOutput();
}

[
    'priceInput',
    'shippingCost',
    'salesTax',
    'featured',
    'togglePriceMode',
].forEach((id) => {
    const element = document.getElementById(id) as HTMLInputElement;
    element.addEventListener(element.type === 'checkbox' ? 'change' : 'input', updateAll);
});

updateAll();
