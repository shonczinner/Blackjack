def get_integer(prompt, s_exit = 'exit'):
    """
    Prompt the user for an integer input.

    Args:
        prompt (str): The prompt message displayed to the user.
        s_exit (str, optional): The string that, if entered by the user, will cause the function to exit. 
                                Defaults to 'exit'.

    Returns:
        int or str: If the user enters an integer, returns the integer value. 
                    If the user enters the exit string (s_exit), returns the string. 
    """  
    while True:
        try:
            value = input(prompt)
            if value == s_exit:
                return value
            else:
                return int(value)
        except ValueError:
            print(f"Please enter a valid integer or {s_exit} to exit"+"\n")

def get_positive_integer(prompt, k):
    """
    Prompt the user for a positive integer input within a specified range.

    Args:
        prompt (str): The prompt message displayed to the user.
        k (int): The upper bound of the allowed range (inclusive).

    Returns:
        int: A positive integer value within the range [0, k].

    Raises:
        ValueError: If the user enters a non-integer value or a value outside the specified range.
    """
    while True:
        try:
            value = int(input(prompt))
            if 0 <= value <= k:
                return value
            else:
                print(f"Please enter an integer between 0 and {k}.")
        except ValueError:
            print("Please enter a valid integer.")

def get_selection(prompt, options):
    """
    Prompt the user to select an option from a list of available options.

    Args:
        prompt (str): The prompt message displayed to the user.
        options (list): A list of strings representing the available options.

    Returns:
        str: The selected option.

    Raises:
        None
    """
    while True:
      value = input(prompt)
      if value in options:
          return value
      else:
          option_str = ', '.join(['\''+x+'\'' for x in options])
          print(f"Please enter one of the options [{option_str}].")
