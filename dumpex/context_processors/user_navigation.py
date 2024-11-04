# context_processors/user_navigation.py

def user_navigation(request):
    navigation = []
    wallet_menu = []
    more = []
    if request.user.is_authenticated:
        user_type = request.user.user_type  # Assuming user_type is an integer
        if user_type == 1:  # Customer
            navigation = [
                {'name': 'DASHBOARD', 'url': 'customer:customer_dashboard', 'icon': 'fas fa-tachometer-alt'}, 
                {'name': 'BOOKING', 'url': 'customer:slot_booking', 'icon': 'fa fa-calendar-plus'},
                {'name': 'VIEW BOOKINGS', 'url': 'customer:view_bookings', 'icon': 'fa fa-calendar-alt'},
                {'name': 'WALLET', 'url': '', 'icon': 'fa fa-wallet'},
                {'name': 'NOTIFICATIONS', 'url': 'customer:notifications', 'icon': 'fa fa-bell'},
                {'name': 'LOGOUT', 'url': 'logout', 'icon': 'fas fa-sign-out-alt'},
            ]
            wallet_menu = [
                {'name': 'BALANCE', 'url': 'wallet:view_balance', 'icon': 'fa fa-wallet'},
                {'name': 'WITHDRAW', 'url': 'wallet:withdraw_money', 'icon': 'fa fa-money-bill-wave'},
                {'name': 'TRANSACTIONS', 'url': 'wallet:transaction_history', 'icon': 'fa fa-exchange-alt'},
            ]
        
        elif user_type == 2:  # Employee
            navigation = [

                {'name': 'DASHBOARD', 'url': 'employee:employee_dashboard', 'icon': 'fas fa-tachometer-alt'}, 
                {'name': 'SHEDULES', 'url': 'employee:view_schedule', 'icon': 'fa fa-calendar-alt'},
                {'name': 'VERIFY USER', 'url': 'employee:verify_user_list', 'icon': 'fa fa-user-check'},
                {'name': 'NOTIFICATION', 'url': 'employee:notification_manager', 'icon': 'fa fa-bell'},
                {'name': 'MORE', 'url': '', 'icon': 'fas fa-ellipsis-h'},
                {'name': 'LOGOUT', 'url': 'logout', 'icon': 'fas fa-sign-out-alt'},
            ]
            more =[
                {'name': 'MANAGER NOTIFICATION', 'url': 'employee:view_manager_notifications', 'icon': 'fa fa-envelope-open-text'},
                {'name': 'VERIFIED USER', 'url': 'employee:verified_user_list', 'icon': 'fa fa-users'},
                {'name': 'SEND TO MANAGER', 'url': 'employee:send_notification_to_manager', 'icon': 'fa fa-paper-plane'},

            ]
            
            
        elif user_type == 3:  # Manager
            navigation = [

                {'name': 'DASHBOARD', 'url': 'manager:manager_dashboard', 'icon': 'fas fa-tachometer-alt'},
                {'name': 'CREATE EMP', 'url': 'manager:create_employee', 'icon': 'fas fa-user-plus'},
                {'name': 'VERIFY EMP', 'url': 'manager:verify_employee_list', 'icon': 'fas fa-user-check'},
                {'name': 'WALLET', 'url': '', 'icon': 'fa fa-wallet'},
                {'name': 'MORE', 'url': '', 'icon': 'fas fa-ellipsis-h'},
                
                {'name': 'LOGOUT', 'url': 'logout', 'icon': 'fas fa-sign-out-alt'},
            ]

            wallet_menu = [
                {'name': 'WALLET', 'url': 'wallet:manager_wallet', 'icon': 'fas fa-wallet'},
                {'name': 'APPROVE WITHDRAW', 'url': 'wallet:withdraw_approval', 'icon': 'fas fa-exchange-alt'},
            ]

            more = [

                {'name': 'VERIFIED EMP', 'url': 'manager:verified_employee_list', 'icon': 'fas fa-users'},
                {'name': 'NOTIFICATION', 'url': 'manager:manager_notifications', 'icon': 'fas fa-bell'},
            ]
            
        elif user_type == 4:  # Admin
            navigation = [
                {'name': 'DASHBOARD', 'url': 'employee:admin_dashboard', 'icon': 'fas fa-tachometer-alt'},
                {'name': 'WALLET', 'url': 'wallet:view_balance', 'icon': 'fa fa-wallet'},
                {'name': 'ADD MONEY', 'url': 'wallet:add_money_to_admin_wallet', 'icon': 'fa fa-plus-circle'},
                {'name': 'SEND MONEY', 'url': 'wallet:send_money', 'icon': 'fa fa-paper-plane'},
                {'name': 'LOGOUT', 'url': 'logout', 'icon': 'fas fa-sign-out-alt'},
            ]
            
    else:
        navigation = [
            
            {'name': 'Register', 'url': '#', 'icon': 'fas fa-user-plus'},
            {'name': 'Login', 'url': 'login', 'icon': 'fas fa-sign-in-alt'},
        ]
    

    return {
        'navigation': navigation,
        'wallet_menu': wallet_menu,
        'more':more,
    }
