from .generators import get_buyer_dtls


def to_buyer(gst_info, place_of_supply):
    addr1 = "{floor}, {street}".format(
        floor=gst_info["AddrFlno"], street=gst_info["AddrSt"]
    )
    return get_buyer_dtls(
        gstin=gst_info["Gstin"],
        lgl_nm=gst_info["LegalName"],
        addr1=addr1,
        pos=place_of_supply,
        loc=gst_info["AddrLoc"],
        pin=gst_info["AddrPncd"],
        stcd=str(gst_info["StateCode"]),
    )
