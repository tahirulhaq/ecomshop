console.log("Sanity check!");

// Get Stripe publishable key
fetch("/config/")
.then((result) => { return result.json(); })
.then((data) => {
  // Initialize Stripe.js
  const stripe = Stripe(data.publicKey);



  fetch("/create-checkout-session/")
  .then((result) => { return result.json(); })
  .then((data) => {
    console.log(data);
    // Redirect to Stripe Checkout
    return stripe.redirectToCheckout({sessionId: data.sessionId})
  })
  .then((res) => {
    console.log(res);
  });
  // Event handler
  document.addEventListener("load", () => {
    // Get Checkout Session ID
    console.log('loaded auto')
    // fetch("/create-checkout-session/")
    // .then((result) => { return result.json(); })
    // .then((data) => {
    //   console.log(data);
    //   // Redirect to Stripe Checkout
    //   return stripe.redirectToCheckout({sessionId: data.sessionId})
    // })
    // .then((res) => {
    //   console.log(res);
    // });
  });//event handler ends here
});