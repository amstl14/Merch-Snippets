// Set the application ID
var applicationId = "";
// var applicationId = "";

// Set the location ID
var locationId = "";
// var locationId = "";


/*
 * function: requestCardNonce
 *
 * requestCardNonce is triggered when the "Pay with credit card" button is
 * clicked
 *
 * Modifying this function is not required, but can be customized if you
 * wish to take additional action when the form button is clicked.
 */
function requestCardNonce(event) {
    $('#submit_handle').click(); //<-- Why is this here?
    // Don't submit the form until SqPaymentForm returns with a nonce
    event.preventDefault();
    // Request a nonce from the SqPaymentForm object
    paymentForm.requestCardNonce();

    return true;
}

// Create and initialize a payment form object
var paymentForm = new SqPaymentForm({

    // Initialize the payment form elements
    applicationId: applicationId,
    locationId: locationId,
    inputClass: 'sq-input',

    // Customize the CSS for SqPaymentForm iframe elements
    inputStyles: [{
        fontSize: '14px'
    }],
    // Initialize Apple Pay placeholder ID
    applePay: {
        elementId: 'sq-apple-pay'
    },

    // Initialize Masterpass placeholder ID
    masterpass: {
        elementId: 'sq-masterpass'
    },
    // Initialize the credit card placeholders
    cardNumber: {
        elementId: 'sq-card-number',
        placeholder: '•••• •••• •••• ••••'
    },
    cvv: {
        elementId: 'sq-cvv',
        placeholder: 'CVV'
    },
    expirationDate: {
        elementId: 'sq-expiration-date',
        placeholder: 'MM/YY'
    },
    postalCode: {
        elementId: 'sq-postal-code',
        placeholder: '90210'
    },

    // SqPaymentForm callback functions
    callbacks: {

        /*
         * callback function: methodsSupported
         * Triggered when: the page is loaded.
         */
        methodsSupported: function (methods) {

            var applePayBtn = document.getElementById('sq-apple-pay');
            var applePayLabel = document.getElementById('sq-apple-pay-label');
            var masterpassBtn = document.getElementById('sq-masterpass');
            var masterpassLabel = document.getElementById('sq-masterpass-label');

            // Only show the button if Apple Pay for Web is enabled
            // Otherwise, display the wallet not enabled message.
            if (methods.applePay === true) {
                applePayBtn.style.display = 'inline-block';
                applePayLabel.style.display = 'none';
            }
            // Only show the button if Masterpass is enabled
            // Otherwise, display the wallet not enabled message.
            if (methods.masterpass === true) {
                masterpassBtn.style.display = 'inline-block';
                masterpassLabel.style.display = 'none';
            }
        },

        /*
         * callback function: createPaymentRequest
         * Triggered when: a digital wallet payment button is clicked.
         */
        createPaymentRequest: function () {

            var paymentRequestJson;
            /* ADD CODE TO SET/CREATE paymentRequestJson */
            return paymentRequestJson;
        },

        /*
         * callback function: validateShippingContact
         * Triggered when: a shipping address is selected/changed in a digital
         *                 wallet UI that supports address selection.
         */
        validateShippingContact: function (contact) {

            var validationErrorObj;
            /* ADD CODE TO SET validationErrorObj IF ERRORS ARE FOUND */
            return validationErrorObj;
        },

        /*
         * callback function: cardNonceResponseReceived
         * Triggered when: SqPaymentForm completes a card nonce request
         */
        cardNonceResponseReceived: function (errors, nonce, cardData, billingContact, shippingContact) {

            var error_arr = [];
            var idx = 0;

            if (errors) {
                // Click the payment button (in checkout modal) to display the fields that had an error
                $('#checkoutPaymentHref').trigger("click");

                // Log errors from nonce generation to the Javascript console
                console.log("Encountered errors:");
                var error_str = "";
                errors.forEach(function (error) {
                    error_arr[idx] = (error.message + '<br>\n');
                    error_str += (error.message + '<br>\n');
                    idx++;
                });
                // Display notification informing of errors
                toastr.options = {
                    "closeButton": false,
                    "debug": false,
                    "newestOnTop": false,
                    "progressBar": false,
                    "positionClass": "toast-bottom-center",
                    "preventDuplicates": true,
                    "onclick": null,
                    "showDuration": "500",
                    "hideDuration": "1000",
                    "timeOut": "2000",
                    "extendedTimeOut": "1000",
                    "showEasing": "swing",
                    "hideEasing": "linear",
                    "showMethod": "fadeIn",
                    "hideMethod": "fadeOut"
                };
                toastr["error"](error_str);
                console.log(error_arr.join(""));
                return;
            }

            // This is our AJAX call to actually attempt to charge the card.
            // If we've gotten here, then our validation and Square Pay's validation passed.
            chargeCard(nonce);
        },

        /*
         * callback function: unsupportedBrowserDetected
         * Triggered when: the page loads and an unsupported browser is detected
         */
        unsupportedBrowserDetected: function () {
            /* PROVIDE FEEDBACK TO SITE VISITORS */
        },

        /*
         * callback function: inputEventReceived
         * Triggered when: visitors interact with SqPaymentForm iframe elements.
         */
        inputEventReceived: function (inputEvent) {
            switch (inputEvent.eventType) {
                case 'focusClassAdded':
                    /* HANDLE AS DESIRED */
                    break;
                case 'focusClassRemoved':
                    /* HANDLE AS DESIRED */
                    break;
                case 'errorClassAdded':
                    /* HANDLE AS DESIRED */
                    break;
                case 'errorClassRemoved':
                    /* HANDLE AS DESIRED */
                    break;
                case 'cardBrandChanged':
                    /* HANDLE AS DESIRED */
                    break;
                case 'postalCodeChanged':
                    /* HANDLE AS DESIRED */
                    break;
            }
        },

        /*
         * callback function: paymentFormLoaded
         * Triggered when: SqPaymentForm is fully loaded
         */
        paymentFormLoaded: function () {

        }
    }
});
