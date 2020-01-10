def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')

    # Transactions
    config.add_route('transaction.create', '/transaction/create')
    config.add_route('transaction.list', '/transaction/')
    config.add_route('transaction.detail', '/transaction/{transaction_id}')
    config.add_route('transaction.update', '/transaction/{transaction_id}/update')
    config.add_route('transaction.delete', '/transaction/{transaction_id}/delete')
