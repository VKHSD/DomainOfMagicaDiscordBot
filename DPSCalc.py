#                    )      )   (      (      
#                 ( /(   ( /(   )\ )   )\ )   
#       (   (     )\())  )\()) (()/(  (()/(   
#       )\  )\  |((_)\  ((_)\   /(_))  /(_))  
#      ((_)((_) |_ ((_)  _((_) (_))   (_))_   
#      \ \ / /  | |/ /  | || | / __|   |   \  
#       \ V /     ' <   | __ | \__ \   | |) | 
#        \_/     _|\_\  |_||_| |___/   |___/  



def calculate_damage(min_damage, max_damage, attack):
    raw_damage = (min_damage + max_damage - 2) / 2
    adjusted_damage = raw_damage * ((attack + 25) / 50)
    return adjusted_damage


def calculate_actual_damage(base_damage, defense):
    actual_damage = max(base_damage - defense, base_damage * 0.1)
    return actual_damage


def calculate_attacks_per_second(dexterity, base_rate_of_fire):
    attacks_per_second = base_rate_of_fire * (6.5 * (dexterity + 17.3) / 75)
    return attacks_per_second


def calculate_dps(min_damage, max_damage, num_projectiles, base_rate_of_fire, attack, dexterity):
    base_damage = calculate_damage(min_damage, max_damage, attack)
    actual_damage = calculate_actual_damage(base_damage, 0)
    attacks_per_second = calculate_attacks_per_second(dexterity, base_rate_of_fire)
    dps = actual_damage * num_projectiles * attacks_per_second
    return dps


def dps_calculator(min_damage, max_damage, num_projectiles, base_rate_of_fire, attack, dexterity):
    for defense in range(0, 101, 10):
        dps = calculate_dps(min_damage, max_damage, num_projectiles, base_rate_of_fire, attack, dexterity)
        print(f'DPS for defense {defense}: {dps}')

