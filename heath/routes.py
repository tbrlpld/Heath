def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('transaction_create', '/create')
    config.add_route('transactions_list', '/list')
    config.add_route('transaction_detail', '/detail/{transaction_id}')
    config.add_route('transaction_edit', '/edit/{transaction_id}')
    config.add_route('transaction_delete', '/delete/{transaction_id}')
