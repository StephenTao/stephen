# 70-highlander.sh - DevStack extras script to install Highlander

if is_service_enabled highlander; then
    if [[ "$1" == "source" ]]; then
        # Initial source
        source $TOP_DIR/lib/highlander
    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing highlander"
        install_highlander
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring highlander"
        configure_highlander
        create_highlander_accounts
    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        echo_summary "Initializing highlander"
        init_highlander
        start_highlander
    fi

    if [[ "$1" == "unstack" ]]; then
        stop_highlander
    fi
fi
