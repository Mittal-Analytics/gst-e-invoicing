from .generators import get_buyer_dtls


def to_buyer(gst_info, place_of_supply):
    parts = [
        gst_info["AddrBnm"],
        gst_info["AddrBno"],
        gst_info["AddrFlno"],
        gst_info["AddrSt"],
    ]
    addr1 = ", ".join(part.strip() for part in parts if part and part.strip())
    return get_buyer_dtls(
        gstin=gst_info["Gstin"],
        lgl_nm=gst_info["LegalName"],
        addr1=addr1,
        pos=place_of_supply,
        loc=gst_info["AddrLoc"],
        pin=gst_info["AddrPncd"],
        stcd=str(gst_info["StateCode"]),
    )
