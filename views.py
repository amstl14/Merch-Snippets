# Django Libs...
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.http import HttpResponse
from django.template import loader
from django.db.models import Q

# Self/Ludega Art includes
from ludega_art.templatetags import ludega_art_filters
from ludega_art.models import customer_order
from ludega_art.models import order_detail
from ludega_art.models import product_type
from ludega_art.models import top_product
from ludega_art.models import product
from ludega_art.models import color
from ludega_art.models import price
from ludega_art.models import image
from ludega_art.models import size
import ludega_art.utils as utils

# Manages the cart (by IP address)
from cart.cart import Cart

# Helpful python libs
from email.mime.text import MIMEText
import unirest
import json
import uuid
import logging
import datetime
import urllib2
import random, string
import smtplib
import inspect
import time


def checkDenverZip(request):
    denver_zip_codes = [80002, 80003, 80004, 80005, 80007, 80010, 80011, 80012, 80013, 80014, 80015, 80016, 80017,
                        80018, 80019, 80020, 80021, 80022, 80023, 80024, 80030, 80031, 80033, 80045, 80101, 80102,
                        80103, 80104, 80105, 80107, 80108, 80109, 80110, 80111, 80112, 80113, 80116, 80117, 80118,
                        80120, 80121, 80122, 80123, 80124, 80125, 80126, 80127, 80128, 80129, 80130, 80131, 80134,
                        80135, 80136, 80137, 80138, 80202, 80203, 80204, 80205, 80206, 80207, 80209, 80210, 80211,
                        80212, 80214, 80215, 80216, 80218, 80219, 80220, 80221, 80222, 80223, 80224, 80226, 80227,
                        80228, 80229, 80230, 80231, 80232, 80233, 80234, 80235, 80236, 80237, 80238, 80239, 80241,
                        80246, 80247, 80249, 80260, 80264, 80290, 80293, 80294, 80401, 80403, 80419, 80420, 80421,
                        80422, 80425, 80427, 80432, 80433, 80436, 80438, 80439, 80440, 80444, 80448, 80449, 80452,
                        80453, 80454, 80456, 80457, 80465, 80470, 80475, 80476, 80601, 80602, 80640, 80820, 80827,
                        80830, 80835]

    check_for_denver_zip = denver_zip_codes.count(int(request))

    return check_for_denver_zip

def contact_us_form_submitted(request):
    # Make sure everything isn't blank
    if request.POST["name"] == "" and request.POST["email"] and request.POST["phone_number"] == "" and request.POST[
        "message"] == "":
        sent_email = utils.send_email('merch.management@ludega.com', "LUDEGA MERCH - Contact Us Form Submitted", '', '',
                                      'All fields were blank.', 'text/plain')

    # Everything wasn't blank. Send contents of user input fields in a
    else:
        to = 'software.support@ludega.com'
        message = 'Contact Us Form Submitted\n\n' \
                  'Name: ' + request.POST["name"] + '\n' \
                                                    'Email: ' + request.POST["email"] + '\n' \
                                                                                        'Phone Number: ' + request.POST[
                      "phone_number"] + '\n' \
                                        'Message: ' + request.POST["message"]

        # Build body of the email
        sent_email = utils.send_email('merch.management@ludega.com', 'LUDEGA MERCH - Contact Us Form Submitted', '', '',
                                      message, 'text/plain')

    response = HttpResponse()
    if (sent_email):
        response.write('Success')
    else:
        response.write('False')
    return response


# TODO: We probably won't have (promotional) events (page) for quite some time. So this can go...
# def events(request):
#     # Set the template for this view to, eventually, return
#     template = loader.get_template('ludega_art/events.html')
#
#     # Build context variables which template will have access to
#     context = {}
#
#     # Return/render the template with the context and request
#     return HttpResponse(template.render(context, request))

def order_confirmation(request):
    query = request.GET.get('order_id_hash')
    order_id_hash = format(query)

    order_info = customer_order.objects.get(order_id_hash=order_id_hash)
    first_name = order_info.firstName
    last_name = order_info.lastName
    address1 = order_info.address1
    address2 = order_info.address2
    city = order_info.city
    state = order_info.state
    zipcode = order_info.zip
    country = order_info.country
    shipping_cost = order_info.shipping_cost
    shipping_method = order_info.shipping_method
    total_price = order_info.total_price
    order_time = order_info.order_time
    order_fulfilled = order_info.order_fulfilled
    email = order_info.email
    sales_tax = order_info.sales_tax
    order_price = order_info.order_price
    order_id = order_info.id
    order_id_hash = order_info.order_id_hash

    if checkDenverZip(zipcode) == 1:
        shipping_cost = 0.00

    template = loader.get_template('ludega_art/order_confirmation.html')
    context = {
        'order_id': order_id,
        'first_name': first_name,
        'last_name': last_name,
        'address1': address1,
        'address2': address2,
        'city': city,
        'state': state,
        'zipcode': zipcode,
        'country': country,
        'shipping_cost': shipping_cost,
        'shipping_method': shipping_method,
        'total_price': total_price,
        'order_time': order_time,
        'order_fulfilled': order_fulfilled,
        'email': email,
        'sales_tax': sales_tax,
        'order_price': order_price,
        'order_id_hash': order_id_hash,

    }

    return HttpResponse(template.render(context, request))


def index(request):
    # Get the products that will be shown at the top
    top_products_name_list = top_product.objects.all()
    top_products_list = []
    for prod_name in top_products_name_list:
        top_products_list.append(product.objects.get(name=prod_name))

    # Get product types & colors
    # These will be used as options for filtering down all the products we offer
    types = product_type.objects.all().order_by('display_name')
    colors = color.objects.all()
    products = product.objects.all().order_by('order')
    prices = price.objects.all()
    images = image.objects.all()
    # These are usable in javascript
    prod_list = product.objects.values_list('id', 'name', 'product_type__display_name', 'image_file', 'colors__name',
                                            'image__name')
    products_json = json.dumps(list(prod_list), cls=DjangoJSONEncoder)
    cart_count = init_get_cart_count(request)

    # These didn't end up being needed
    # img_list      = image.objects.values_list('id', 'name')
    # images_json   = json.dumps(list(img_list), cls=DjangoJSONEncoder)
    # color_list    = color.objects.values_list('id', 'name')
    # colors_json   = json.dumps(list(color_list), cls=DjangoJSONEncoder)
    # type_list     = product_type.objects.values_list('id', 'display_name')
    # types_json    = json.dumps(list(type_list), cls=DjangoJSONEncoder)

    # Set the template for this view to, eventually, return
    template = loader.get_template('ludega_art/index.html')

    # Build context variables which template will have access to
    context = {
        'top_products_list': top_products_list,
        'types': types,
        'colors': colors,
        'products': products,
        'prices': prices,
        'images': images,
        'products_json': products_json,
        'cart_count': cart_count,
        'show_age_verification': show_age_verification(request),
    }

    # Return/render the template with the context and request
    return HttpResponse(template.render(context, request))


# This view returns a JSON formatted string which contains the
# 'id', 'name', 'description', 'product_type__display_name', 'image_file', 'image__name'
# of any products which match the filter options passed into the function
# via a string (which contains ":-!" delimited filter options)
def filter_request(request):
    # Getting/Saving the filters string (from the request) as a string
    filters = request.POST["filters"]

    # Separating out the filters string
    # filter_sections[0] = images
    # filter_sections[1] = clothing
    # filter_sections[2] = products
    # filter_sections[3] = colors
    filter_sections = filters.split(":-!")
    images = filter_sections[0].split(",")
    # Clothing filter merged with products
    # clothing = filter_sections[1].split(",");
    products = filter_sections[1].split(",")
    # Color Filters Disabled for Now
    # colors = filter_sections[3].split(",");

    # Building query string segments
    query_string = "product.objects.filter("

    # len should never be 0, if it is, we'll treat it the same as "All"
    # check box being checked
    if len(images) != 0 and images[0] != "All" and images[0] != "":
        # Create statements that translate to
        # image="Something" OR image="SomethingElse" etc...
        i = 0
        while i < len(images):
            query_string += "Q(image__name=\"" + images[i] + "\")"
            if i + 1 < len(images):
                query_string += "| "
            i += 1

        # "," is "and" once converted to sql
        query_string += ", "

    # Color Filter Disabled for Now
    # OLD CODE FOR COLOR FILTER...
    # if len(colors) != 0 and colors[0] != "All":
    #    i = 0
    #    while i < len(colors):
    #        query_string += "Q(colors__name=\"" + colors[i] + "\")"
    #        if i+1 < len(colors):
    #            query_string += "| "
    #        i += 1
    #
    #    # "," is "and" once converted to sql
    #    query_string += ", "
    ###########################################

    # Handle for product filter settings
    if len(products) != 0 and products[0] != "All" and products[0] != "":
        # Create statements that translate to
        # product="Something" OR product="SomethingElse" etc...
        i = 0
        while i < len(products):
            query_string += "Q(product_type__display_name=\"" + products[i] + "\")"
            if i + 1 < len(products):
                query_string += "| "
            i += 1

        # "," is "and" once converted to sql
        # query_string += ", "

    # Handle for clothing/product filter settings
    # OLD CODE FOR CLOTHING/PRODUCT FILTER...
    # We merged the two filters as we found it confusing for users trying to filter products.
    # if clothing[0] == "":
    #    query_string += "Q(product_type__is_clothing=\"False\")"
    #    # "," is "and" once converted to sql
    #    query_string += ", "
    # elif clothing[0] != "All":
    #    if clothing[0] == "":
    #        query_string += "Q(product_type__is_clothing=\"False\")"
    #    else:
    #        i = 0
    #        while i < len(clothing):
    #            query_string += "Q(product_type__display_name=\"" + clothing[i] + "\")"
    #            if i+1 < len(clothing):
    #                query_string += "| "
    #            i += 1
    #    if products[0] != "All":
    #        # This one needs to be an or because they are both product types specifiers
    #        query_string += "| "
    #    else:
    #        query_string += "| "
    #        query_string += "Q(product_type__is_clothing=\"False\")"
    # if products[0] != "All":
    #    i = 0
    #    while i < len(products):
    #        query_string += "Q(product_type__display_name=\"" + products[i] + "\")"
    #        if i+1 < len(products):
    #            query_string += "| "
    #        i += 1
    #
    #    if clothing[0] == "All":
    #        query_string += "| "
    #        query_string += "Q(product_type__is_clothing=\"True\")"
    ##################################################################

    # Finalize the query
    query_string += ").order_by('order').values_list('id', 'name', 'description', 'product_type__display_name', 'image_file', 'image__name')"

    # Evaluate the query that we built (above)
    prod_list = eval(query_string)

    # Convert list to json
    # products_json = json.dumps(list(prod_list), cls=DjangoJSONEncoder)

    products_json_data = json.loads(json.dumps(list(prod_list)))
    for elm in products_json_data:
        price_str = ludega_art_filters.get_price_str(elm[0])
        elm.append(price_str)

    products_json = json.dumps(products_json_data, cls=DjangoJSONEncoder)

    response = HttpResponse()
    # This is for debug purposes...
    # response.write(query_string)
    # This is actual response/return
    response.write(products_json)
    return response


def submit_order_charge_card(request):
    # Get this function's name (for logging purposes)
    frame = inspect.currentframe()
    this_func_name = inspect.getframeinfo(frame).function

    # Debug output
    logging.warning(this_func_name + " - request was: " + request.body)

    # TODO: Request should just send the cart (as a JSON string) and we should parse that json string here.
    # Right now what we're doing is parsing it in javascript and then (again...) parsing it here. Just seems like
    # doubled up "work" for the computer(s)

    # Loading network request vars (json) into local python variables
    nonce = request.POST["nonce"]
    number_of_keys = int(request.POST["number_of_keys"])
    quantity_arr = request.POST.getlist("quantity_arr[]")
    prod_id_arr = request.POST.getlist("prod_id_arr[]")
    prod_type_arr = request.POST.getlist("prod_type_arr[]")
    prod_size_arr = request.POST.getlist("prod_size_arr[]")
    first_name = request.POST["first_name"]
    last_name = request.POST["last_name"]
    address1 = request.POST["address1"]
    address2 = request.POST["address2"]
    city = request.POST["city"]
    state = request.POST["state"]
    zip = request.POST["zip"]
    country = request.POST["country"]
    email = request.POST["email"]
    note = request.POST["note"]
    shipping_method = request.POST["shipping_method"]

    # Bunch of debug outpoot
    print('fName: ' + first_name)
    print('lName: ' + last_name)
    print('Addr L1: ' + address1)
    print('Addr L2: ' + address2)
    print('City: ' + city)
    print('State: ' + state)
    print('Zip: ' + zip)
    print('# of Keys: ' + str(number_of_keys))
    print('Quant Arr: ' + str(quantity_arr))
    print('Prod ID Arr: ' + str(prod_id_arr))
    print('Prod Type Arr: ' + str(prod_type_arr))
    print('Prod Size Arr: ' + str(prod_size_arr))

    # Loop over items (that were in cart) and add up total cost (aka price)
    # Note: This exists client (aka browser) side. However, for security purposes, we are re-calculating price (aka cost)
    # here so that someone can't make an ajax request to our server and claim that the price is $1 when it's really $100.
    calculated_price = 0
    price_arr = [0] * number_of_keys
    for x in range(0, number_of_keys):
        prod_type_obj = product_type.objects.get(name=prod_type_arr[x])
        size_obj = size.objects.get(name=prod_size_arr[x])
        price_obj = price.objects.get(size=size_obj, product_type=prod_type_obj)
        item_price = float(price_obj.price)
        price_arr[x] = item_price
        item_quantity = float(quantity_arr[x])
        calculated_price += (item_price * item_quantity)
        print('Prod Name: ' + prod_type_arr[x])
        print('Summed Price (so far): ' + str(calculated_price))

    # Calc sales tax now that we have calculated price
    sales_tax = (calculated_price*0.029)

    # Try to create (and save) instance of order (given information above) and order details
    try:

        shipping_cost = 9.00

        # Get shipping cost
        if (shipping_method is '0'):
            shipping_method = "USPS Priority"
            shipping_cost = 9.00


        if checkDenverZip(zip) == 1:
            shipping_cost = 0.00

        shipping_cost = float("{0:.2f}".format(shipping_cost))

        # Debug Output
        print('Sales Tax Cost: ' + str(calculated_price + sales_tax))
        print('Prod Cost: ' + str(calculated_price + sales_tax))
        print('Total Prod Cost + Sales Tax (as int (aka x10^2)): ' + str(int((calculated_price + sales_tax) * 100)))
        # print('Total Prod Cost + Sales Tax + Shipping (as int (aka x10^2)): ' + str(int((calculated_price + shipping_cost + sales_tax) * 100)))

        # Create order id hash (aka order confirmation #)
        is_unique = False
        while not is_unique:
            id_hash = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))

            # Ensure that this order id hash doesn't exist already in the db (aka make sure it's unique)
            orders_rslt_set = customer_order.objects.filter(order_id_hash=id_hash)
            if(len(orders_rslt_set) == 0):
                is_unique = True

        order = customer_order(email=email, customer_note=note, firstName=first_name, lastName=last_name, address1=address1,
                               address2=address2, city=city, state=state, zip=zip, country=country,
                               shipping_method=shipping_method, shipping_cost=shipping_cost,
                               order_price=calculated_price,
                               sales_tax=sales_tax, total_price=(calculated_price + shipping_cost + sales_tax),
                               order_time=datetime.datetime.now(), order_fulfilled=False, order_id_hash=id_hash)

        # Save/write it to the db
        order.save()

        # List for storing the order details (of the above order). This will be handy (aka save us a db call) later on
        # if we end up needing to delete the order details (and order)
        order_details = list()
        # Create order details and push them onto list (above)
        for idx in range(0, number_of_keys):
            prod_size = size.objects.get(name=prod_size_arr[idx]) # Needed twice in below initialization
            prod_type = product_type.objects.get(name=prod_type_arr[idx]) # Needed twice in below initialization
            detail = order_detail(product=product.objects.get(id=prod_id_arr[idx]),
                                   product_type=prod_type,
                                   product_size=prod_size,
                                   product_quantity=quantity_arr[idx],
                                   item_price=price.objects.get(size=prod_size, product_type=prod_type),
                                   customer_order=order)
            detail.save()
            # Adding to list of details. This will be used should we (later on in this func) need to delete them
            order_details.append(detail)

    except ValueError as e:
        # Print/log the error/exceptions
        logging.error(this_func_name + " - " + str(e))
        # We failed to save and/or create the order for some reason.
        utils.send_email("merch.management@ludeag.com",
                         "[CRITICAL ERROR] - " + this_func_name, '', '',
                         "CRITICAL ERROR - " + this_func_name + " - Failed to create and/or save instance of order and/or order details."
                         "\nException/Error was: " + str(e) +""
                         "\nNetwork request/data sent to this function was " + request.body +""
                         "\nNOTE: STILL ATTEMPTING CARD CHARGE!", "plain")

    # Vars needed for charging card.
    card_nonce = nonce
    location_id = ""
    access_token = ""
    # location_id = ""
    # access_token = ""

    # Attempt to charge the card
    charge_attempt_response = unirest.post('https://connect.squareup.com/v2/locations/' + location_id + '/transactions',
                                           headers={
                                               'Accept': 'application/json',
                                               'Content-Type': 'application/json',
                                               'Authorization': 'Bearer ' + access_token,
                                           },
                                           params=json.dumps({
                                               'card_nonce': card_nonce,
                                               'amount_money': {
                                                   'amount': int(((calculated_price + shipping_cost + sales_tax) * 100)),
                                                   'currency': 'USD'
                                               },
                                               'idempotency_key': str(uuid.uuid1())
                                           })
                                           )

    print(charge_attempt_response.body)

    # TODO: If for some reason we get here and receive the following response from Square Pay:
    #   {u'errors': [{u'category': u'INVALID_REQUEST_ERROR', u'code': u'CARD_TOKEN_USED', u'detail': u'Card nonce already used; please request new nonce.'}]}
    # Then we should request a new nonce and try again. Doing so will involve responding with the message back to the
    # client (aka browser) and then JavaScript properly handling it. Which means, re-requesting a new nonce and then re-calling this funciton via ajax request.
    # If error in charge card response, then
    if "errors" in charge_attempt_response.body:
        # Delete order details (for this order)
        for detail in order_details:
            detail.delete()
        # Delete order that was saved earlier (and all order details)
        order.delete()
        # And give response to client (browser) to handle
        response = HttpResponse()
        response.write(charge_attempt_response.body)
        return response
    else:
        # Send order confirmation email to user (aka customer who just submitted and payed for order)
        template = loader.get_template('ludega_art/order_confirmation.html')
        context = {
            'order_id': order.id,
            'first_name': first_name,
            'last_name': last_name,
            'address1': address1,
            'address2': address2,
            'city': city,
            'state': state,
            'zipcode': zip,
            'country': country,
            'shipping_cost': shipping_cost,
            'shipping_method': shipping_method,
            'total_price': order.total_price,
            'order_time': order.order_time,
            'order_fulfilled': order.order_fulfilled,
            'email': email,
            'sales_tax': order.sales_tax,
            'order_price': order.order_price,
            'order_id_hash': id_hash,
        }
        utils.send_email(email, 'Ludega Merch Order Confirmation', '', '', template.render(context), 'html')

    # Send email to Merch Management Team so they know that a new order was placed (and needs to be process/handled/shipped out)
    order_info_str = 'New Merch Order from User: ' + first_name + ' ' + last_name + ' ' + email + ' where Order_ID_Hash = ' + id_hash
    utils.send_email('software.support@ludega.com', 'New Merch Order: ' + id_hash, '', '', order_info_str, 'html')

    # Give response to client (aka browser) to handle which includes the order hash id
    response = HttpResponse()
    response.write("{\"errors\":\"\",\"order_confirmation_number\":\""+id_hash+"\"}")
    return response


# TODO: Remove this function once new functionality is thoroughly tested out.
def build_order(request):
    try:
        # Get function name (for logging purposes)
        frame = inspect.currentframe()
        this_func_name = inspect.getframeinfo(frame).function

        logging.info(this_func_name + ' - https request was: ' + request.body)

        nonce = request.POST["nonce"]
        number_of_keys = int(request.POST["number_of_keys"])
        quantity_arr = request.POST.getlist("quantity_arr[]")
        prod_id_arr = request.POST.getlist("prod_id_arr[]")
        prod_type_arr = request.POST.getlist("prod_type_arr[]")
        prod_size_arr = request.POST.getlist("prod_size_arr[]")

        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        address1 = request.POST["address1"]
        address2 = request.POST["address2"]
        city = request.POST["city"]
        state = request.POST["state"]
        zip = request.POST["zip"]
        country = request.POST["country"]
        email = request.POST["email"]

        order_id_hash = request.POST["order_id_hash"]

        shipping_option = request.POST["shipping_option"]

        # order_info_str = 'New Merch Order... Product ID: ' + prod_id_arr + ' Product Type: ' + prod_type_arr + ' Product Size: ' + prod_size_arr + \
        #                  ' First Name: ' + first_name + ' Last Name' + last_name + ' Address1: ' + address1 + ' Address2: ' + address2 + ' City: ' + city +\
        #                  ' State: ' + state + ' Zip: ' + zip + ' Country: ' + country + ' Email: ' + email + ' Order_id_hash: ' + order_id_hash + ' Shipping Option: ' + shipping_option

        order_info_str = 'New Merch Order from User: ' + first_name + ' ' + last_name + ' ' + email + ' where Order_ID_Hash = ' + order_id_hash

        utils.send_email('software.support@ludega.com', 'New Merch Order: ' + order_id_hash, '', '', order_info_str,
                         'html')

        print(first_name)
        print(last_name)
        print(address1)
        print(address2)
        print(city)
        print(state)
        print(zip)
        print(number_of_keys)
        print(quantity_arr)
        print(prod_id_arr)
        print(prod_type_arr)
        print(prod_size_arr)


        if (shipping_option == '0'):
            shipping_method = "USPS Priority"
            shipping_cost = 9.00
        if (shipping_option != '0'):
            shipping_method = "Free Shipping"
            shipping_cost = 0.00

        if checkDenverZip(zip) == 1:
            shipping_cost = 0.00

        calculated_price = 0
        price_arr = [0] * number_of_keys
        for x in range(0, number_of_keys):
            print(prod_type_arr[x])
            prod_type_obj = product_type.objects.get(name=prod_type_arr[x])
            size_obj = size.objects.get(name=prod_size_arr[x])
            price_obj = price.objects.get(size=size_obj, product_type=prod_type_obj)
            item_price = float(price_obj.price)
            price_arr[x] = item_price
            item_quantity = float(quantity_arr[x])
            calculated_price += (item_price * item_quantity)
            print(calculated_price)

        print(nonce)
        print(price_arr)

        order = customer_order()

        id_hash = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        print(id_hash)

        print(order.email)
        order.firstName = first_name
        print(order.firstName)
        order.lastName = last_name
        print(order.lastName)
        order.address1 = address1
        print(order.address1)
        order.address2 = address2
        print(order.address2)
        order.city = city
        print(order.city)
        order.state = state
        print(order.state)
        order.zip = zip
        print(order.zip)
        order.country = country
        print(order.country)
        order.shipping_method = shipping_method
        order.shipping_cost = float("{0:.2f}".format(shipping_cost))
        order.order_price = calculated_price
        print(order.order_price)
        order.sales_tax = (calculated_price * 0.029)
        print(order.sales_tax)
        order.total_price = (calculated_price + order.shipping_cost + order.sales_tax)
        print(order.total_price)
        order.order_time = datetime.datetime.now()
        print(order.order_time)
        order.order_fulfilled = False
        print(order.order_fulfilled)
        order.order_id_hash = order_id_hash
        order.save()

        for idx in range(0, number_of_keys):
            details = order_detail()
            details.product = product.objects.get(id=prod_id_arr[idx])
            print(details.product)
            print(prod_type_arr[idx])
            details.product_type = product_type.objects.get(name=prod_type_arr[idx])
            print(details.product_type)
            details.product_size = size.objects.get(name=prod_size_arr[idx])
            print(details.product_size)
            details.product_quantity = quantity_arr[idx]
            print(details.product_quantity)
            details.item_price = price.objects.get(size=details.product_size, product_type=details.product_type)
            print(details.item_price)
            details.customer_order = order
            details.save()

        # Send confirmation email
        template = loader.get_template('ludega_art/order_confirmation.html')
        context = {
            'order_id': order.id,
            'first_name': first_name,
            'last_name': last_name,
            'address1': address1,
            'address2': address2,
            'city': city,
            'state': state,
            'zipcode': zip,
            'country': country,
            'shipping_cost': shipping_cost,
            'shipping_method': shipping_method,
            'total_price': order.total_price,
            'order_time': order.order_time,
            'order_fulfilled': order.order_fulfilled,
            'email': email,
            'sales_tax': order.sales_tax,
            'order_price': order.order_price,
            'order_id_hash': order_id_hash,
        }
        utils.send_email(email, 'Ludega Merch Order Confirmation', '', '', template.render(context), 'html')
        #---------------------------------

        response = HttpResponse()
        response.write('Success')
        return response

    except ValueError as e:
        # Print/log the error/eceptions
        logging.error(this_func_name + " - " + str(e))

        # Send email to software.support@ludega.com warning that error occurred
        utils.send_email('software.support@ludega.com', 'ERROR - Error in ' + this_func_name, '', '', str(e), 'text/plain')

        response = HttpResponse()
        response.write('Internal Server Error: ' + str(e))
        return response


# def starting_at(request):
#    prices = price.objects.get(request['product_type'])
#    lowest_price = prices[0].price
#    for price_ in prices:
#        if lowest_price > price_.price:
#            lowest_price = price_.price
#    return lowest_price

# This server side function compiles all needed information for the product modal
# that the user clicked and returns it in the form of a JSON formatted string.
def get_product_modal_info(request):
    prod_id = request.POST["id"]

    # Get product (by product id passed in post request)
    requested_prod = product.objects.filter(id=prod_id)
    # Save requested prod as list of relevant information for later json formatting
    prod_info = requested_prod.values_list('id', 'name', 'description', 'product_type__display_name', 'image_file',
                                           'image__name')
    # Just making so "[0]" doesn't keep having to be used when working with "requested_prod"
    requested_prod = requested_prod[0]

    # If this product has sub_types, then they need to be listed in our size drop downs.
    product_sub_types = None
    if (len(requested_prod.sub_types.all()) > 0):
        product_sub_types = requested_prod.sub_types.all()

    # Get related product types that we'll be listing as options for size/type dropdowns on
    # product modal. This is found via the image model/object.
    # prod_img_obj = image.objects.filter(name=requested_prod.image)[0]
    # Loop through and get related product types
    # related_prod_type_list = []
    # for related_prod_type in prod_img_obj.product_types.all():
    #    related_prod_type_list.append(related_prod_type)

    purchase_options = {}
    if (product_sub_types is None):
        # Build purchase_options object/json stuffs
        purchase_options[str(requested_prod.product_type.display_name)] = {}
        prod_prices = price.objects.filter(product_type=requested_prod.product_type,
                                           size__in=requested_prod.sizes.all())
        purchase_options[str(requested_prod.product_type.display_name)][
            "description"] = requested_prod.product_type.description
        purchase_options[str(requested_prod.product_type.display_name)]["size_price"] = {}
        # Fill a list with available sizes for this particular product.
        for price_obj in prod_prices:
            purchase_options[str(requested_prod.product_type.display_name)]["size_price"][str(price_obj.size)] = str(
                price_obj.price)
    else:
        # If there are other sub product types, then get their info instead
        for prod_sub_type in product_sub_types:
            prod_prices = price.objects.filter(product_type=prod_sub_type, size__in=requested_prod.sizes.all())
            if (len(prod_prices) > 0):
                purchase_options[prod_sub_type.display_name] = {}
                purchase_options[prod_sub_type.display_name]["description"] = prod_sub_type.description
                purchase_options[prod_sub_type.display_name]["size_price"] = {}
                for price_obj in prod_prices:
                    purchase_options[prod_sub_type.display_name]["size_price"][str(price_obj.size)] = str(
                        price_obj.price)

    # Get related products
    # Related products are defined as products of the same product_type
    related_prods = product.objects.filter(product_type=requested_prod.product_type).exclude(id=prod_id)

    # Building JSON data
    response_data = {}
    response_data['requested_prod'] = {}
    response_data['requested_prod']['id'] = requested_prod.id
    response_data['requested_prod']['product_name'] = requested_prod.name
    response_data['requested_prod']['description'] = requested_prod.description
    response_data['requested_prod']['product_type'] = requested_prod.product_type.name
    response_data['requested_prod']['image_file'] = str(requested_prod.image_file)
    response_data['requested_prod']['image_name'] = requested_prod.image.name
    response_data['purchase_options'] = purchase_options
    response_data['related_prods'] = {}
    for prod in related_prods:
        response_data['related_prods'][prod.name] = {}
        response_data['related_prods'][prod.name]['id'] = prod.id
        response_data['related_prods'][prod.name]['product_name'] = prod.name
        response_data['related_prods'][prod.name]['description'] = prod.description
        response_data['related_prods'][prod.name]['product_type'] = prod.product_type.name
        response_data['related_prods'][prod.name]['image_file'] = str(prod.image_file)
        response_data['related_prods'][prod.name]['image_name'] = prod.image.name

    # Create django/web transfer safe json string out of response data
    prod_info_json = json.dumps(response_data, cls=DjangoJSONEncoder)

    response = HttpResponse()
    response.write(prod_info_json)
    return response


def add_to_cart(request):  # , product_id, quantity):
    product_id = int(request.POST["product_id"])
    quantity = int(request.POST["quantity"])
    price = request.POST["price"]
    p_type = request.POST["type"]
    p_size = request.POST["size"]
    price = float(price.replace("$", ""))
    prod_obj = product.objects.get(id=product_id)

    cart = Cart(request)
    cart.add(prod_obj, price, quantity, p_size, p_type)

    response = HttpResponse()
    response.write("Success")
    return response


def update_cart(request):
    product_id = int(request.POST["product_id"])
    quantity = int(request.POST["quantity"])
    price = request.POST["price"]
    p_type = request.POST["type"]
    p_size = request.POST["size"]
    price = float(price.replace("$", ""))
    prod_obj = product.objects.get(id=product_id)

    cart = Cart(request)
    cart.update(prod_obj, quantity, price, p_size, p_type)

    response = HttpResponse()
    response.write("Success")
    return response


def remove_from_cart(request):
    product_id = request.POST["product_id"]
    prod_size = request.POST["size"]
    prod_type = request.POST["type"]
    prod_obj = product.objects.get(id=product_id)
    cart = Cart(request)
    cart.remove(prod_obj, prod_size, prod_type)

    response = HttpResponse()
    response.write("Success")
    return response


def get_cart(request):
    # Get the cart as an object
    cart = Cart(request)

    # Creating object for storing cart information
    cart_info_json = {}
    # Just keeping track of iterations
    i = 0
    for item in cart:
        prod = item.get_product()
        cart_info_json[str(i)] = {}
        cart_info_json[str(i)]["name"] = prod.name
        cart_info_json[str(i)]["prod_id"] = prod.id
        cart_info_json[str(i)]["img_loc"] = str(prod.image_file)
        cart_info_json[str(i)]["quantity"] = item.quantity
        cart_info_json[str(i)]["type"] = item.prod_type
        cart_info_json[str(i)]["size"] = item.prod_size
        cart_info_json[str(i)]["price"] = item.unit_price

        # Get variant ID for this particular item
        # variant_id_obj = shopfiy_variant_id.objects.filter(product__id=prod.id,size__size=item.prod_size,type__display_name=item.prod_type)
        # cart_info_json[str(i)]["variant_id"] = variant_id_obj[0].variant_id
        i += 1

    # Save total price of cart
    cart_info_json["total_price"] = cart.summary()

    cart_info_json = json.dumps(cart_info_json, cls=DjangoJSONEncoder)

    response = HttpResponse()
    response.write(cart_info_json)
    return response


def init_get_cart_count(request):
    # Get the cart and call its count function
    cart = Cart(request)

    return (str(cart.count()))

def clear_cart(request):
    # Get the cart and call its clear function
    cart = Cart(request)

    # Clear the cart
    cart.clear()

    # Network response success
    response = HttpResponse()
    response.write("{\"error\":\"\",\"message\":\"success\"}")
    return response


def get_cart_count(request):
    # Get the cart and call its count function
    cart = Cart(request)
    cart_count = str(cart.count())
    # Reply with the count
    response = HttpResponse()
    response.write(cart_count)
    return response


def get_price_str(_id):
    # Get the product (given the id)
    product_obj = (product.objects.filter(id=str(_id)))[0]

    # Get product type
    product_type_obj = (product_type.objects.filter(name=product_obj.product_type.name))[0]

    # Get product subtypes
    product_sub_types = None
    if (len(product_obj.sub_types.all()) > 0):
        product_sub_types = product_obj.sub_types.all()

    # If there aren't any sub types, then we can just loop through the prices
    # for this type and find the highest/lowest
    price_str = ""
    if (product_sub_types is None):
        # Get all sizes for this particular product. This will be needed to filter prices.
        prod_sizes = product_obj.sizes.all()
        # Get all prices for this product obj
        prod_prices = price.objects.filter(product_type=product_type_obj, size__in=prod_sizes)

        # Get lowest and highest prices for this product
        lowest = prod_prices[0].price
        highest = prod_prices[0].price
        for _price in prod_prices:
            if _price.price < lowest:
                lowest = _price.price
            if _price.price > highest:
                highest = _price.price

        # Form string
        if lowest != highest:
            price_str = "$" + str(lowest) + " to $" + str(highest)
        else:
            price_str = "$" + str(lowest)
    # If there a   re sub types, then we need to loop through each
    # of the prices listed for each sub type and then we'll get
    # the lowest/highest price
    else:
        lowest = 1000000000
        highest = 0
        # Get all sizes for this particular product. This will be needed to filter prices.
        prod_sizes = product_obj.sizes.all()
        # Get all sizes for this particular product. This will be needed to filter prices.
        product_sub_types = product_obj.sub_types.all()
        for _type in product_sub_types:
            # Get all prices for this product obj
            prod_prices = price.objects.filter(product_type=_type, size__in=prod_sizes)

            # Get lowest and highest prices for this product
            for _price in prod_prices:
                if _price.price < lowest:
                    lowest = _price.price
                if _price.price > highest:
                    highest = _price.price

        # Form string
        if lowest != highest:
            price_str = "$" + str(lowest) + " to $" + str(highest)
        else:
            price_str = "$" + str(lowest)

    response = HttpResponse()
    response.write(price_str)
    return response


# Example on limiting "access" if the user is not logged in.
# def my_view(request):
#    if not request.user.is_authenticated:
#        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

def contact_form_submit(request):
    # Gather the data that's needed to validate the reCaptcha
    ip = request.POST['user_ip']
    captcha = request.POST['captcha']

    # Make POST request to Google checking if the user is a robot.
    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = {'secret': '6LfE2EcUAAAAAPRDw3F6iPw2y1nVwqG3Ejseu9TP',
              'response': captcha}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    data = response.read()

    # If Google's response (to above post request) contains "  "success": true", then go on to send the email.
    # Otherwise return failure
    data_json = json.loads(data)
    if data_json["success"] == True:

        # Build body of the email
        body = "CONTACT FORM SUBMITTED ON \"brokerage.ludega.com\"\n\n"
        body += "Name: " + request.POST['first_name'] + request.POST['last_name'] + "\n"
        body += "Email: " + request.POST['email'] + "\n"
        body += "Message: " + request.POST['message'] + "\n"

        # Create email MIMEText object and fill headers
        email = MIMEText(body)
        email['Subject'] = '[' + datetime.now().strftime(
            "%I:%M%p on %B %d, %Y") + '] [Ludega Brokerage] CONTACT FORM SUBMITTED'
        email['From'] = 'ludega.bot@ludega.com'
        email['To'] = 'ludega.team@ludega.com'

        # Send the email via Google's SMTP server, but don't include the envelope header.
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login('bot.ludega@gmail.com', 'Summ69.+123#@!')
        s.sendmail('bot.ludega@gmail.com', 'alex.woody@ludega.com',
                   email.as_string())  # 'brokerage.team@ludega.com', email.as_string())
        s.quit()

        return HttpResponseRedirect(reverse('index'))

    else:
        return HttpResponse("{\"success\":false,\"message\":\"Google reCaptcha failed.\"}")

# Example on limiting "access" if the user is not logged in.
# def my_view(request):
#    if not request.user.is_authenticated:
#        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))


def no_selected_on_age_verification(request):
    request.session["show_age_verification"] = True
    return HttpResponse("{\"errors\":\"\"}")


def show_age_verification(request):
    # Check if "last_checked_session" timestamp exists for this sessions
    # If ___x___ amount of time (in seconds) has passed (see code for actual amount of time), then we should
    # reset all session variables (except for cart) to their default state.
    if "last_checked_session" not in request.session:
        request.session["last_checked_session"] = time.time()
    elif time.time() - request.session["last_checked_session"] > 86400:
        print(time.time() - request.session["last_checked_session"])
        # Reset all session variables to default below (except cart related stuffs)
        request.session["show_age_verification"] = True
        # Reset timer
        request.session["last_checked_session"] = time.time()

    # Check if we need to show age verification or not
    if "show_age_verification" not in request.session or request.session["show_age_verification"]:
        request.session["show_age_verification"] = False
        return "{\"errors\":\"\",\"show_age_verification\":\"true\"}"
    else:
        return "{\"errors\":\"\",\"show_age_verification\":\"false\"}"
