def _to_camel_case(name):
    return "".join(word.title() for word in name.split("_"))


def _to_camel_case_dict(**kwargs):
    return {_to_camel_case(k): v for k, v in kwargs.items()}


def get_tran_dtls(*, tax_sch="GST", sup_typ="B2B", **kwargs):
    return _to_camel_case_dict(tax_sch=tax_sch, sup_typ=sup_typ, **kwargs)


def get_doc_dtls(*, typ, no, dt, **kwargs):
    return _to_camel_case_dict(typ=typ, no=no, dt=dt, **kwargs)


def get_seller_dtls(*, gstin, lgl_nm, addr1, loc, pin, stcd, **kwargs):
    return _to_camel_case_dict(
        gstin=gstin,
        lgl_nm=lgl_nm,
        addr1=addr1,
        loc=loc,
        pin=pin,
        stcd=stcd,
        **kwargs,
    )


def get_buyer_dtls(*, gstin, lgl_nm, pos, addr1, loc, pin, stcd, **kwargs):
    return _to_camel_case_dict(
        gstin=gstin,
        lgl_nm=lgl_nm,
        pos=pos,
        addr1=addr1,
        loc=loc,
        pin=pin,
        stcd=stcd,
        **kwargs,
    )


def get_disp_dtls(*, nm, addr1, loc, pin, stcd, **kwargs):
    return _to_camel_case_dict(
        nm=nm, addr1=addr1, loc=loc, pin=pin, stcd=stcd, **kwargs
    )


def get_ship_dtls(*, lgl_nm, addr1, loc, pin, stcd, **kwargs):
    return _to_camel_case_dict(
        lgl_nm=lgl_nm, addr1=addr1, loc=loc, pin=pin, stcd=stcd, **kwargs
    )


def get_item(
    *,
    sl_no,
    is_servc,
    hsn_cd,
    unit_price,
    igst_amt,
    tot_amt,
    ass_amt,
    gst_rt,
    tot_item_val,
    **kwargs,
):
    return _to_camel_case_dict(
        sl_no=sl_no,
        is_servc=is_servc,
        hsn_cd=hsn_cd,
        unit_price=unit_price,
        igst_amt=igst_amt,
        tot_amt=tot_amt,
        ass_amt=ass_amt,
        gst_rt=gst_rt,
        tot_item_val=tot_item_val,
        **kwargs,
    )


def get_bch_dtls(*, nm, **kwargs):
    return _to_camel_case_dict(nm=nm, **kwargs)


def get_val_dtls(*, tot_inv_val, **kwargs):
    return _to_camel_case_dict(tot_inv_val=tot_inv_val, **kwargs)


def get_pay_dtls(**kwargs):
    return _to_camel_case_dict(**kwargs)


def get_ewb_dtls(*, distance, **kwargs):
    return _to_camel_case_dict(distance=distance, **kwargs)


def get_invoice(
    *,
    version="1.1",
    tran_dtls,
    doc_dtls,
    seller_dtls,
    buyer_dtls,
    item_list,
    val_dtls,
    ewb_dtls,
    **kwargs,
):
    return _to_camel_case_dict(
        version=version,
        tran_dtls=tran_dtls,
        doc_dtls=doc_dtls,
        seller_dtls=seller_dtls,
        buyer_dtls=buyer_dtls,
        item_list=item_list,
        val_dtls=val_dtls,
        ewb_dtls=ewb_dtls,
        **kwargs,
    )
