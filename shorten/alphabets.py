"""\
:data HEX:                    lowercase hex digits

:data DEFAULT:                the numbers 0-9 and letters a-Z

:data DISSIMILAR:             the same as `DEFAULT` but excludes similar 
                              characters 0, O, 1, l, I
                              (zero, uppercase 'o', one, lowercase 'l'
                              and uppercase 'i')

:data URLSAFE:                the numbers 0-9, letters a-Z and dash, underscore
                              and tilde. All characters considered safe for 
                              URLs.

:data URLSAFE_DISSIMILAR:     the same as `URLSAFE` but excluding similar
                              characters.
"""

HEX = '0123456789abcdef'
DEFAULT = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
DISSIMILAR = '23456790ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
URLSAFE = '0123456789ABCEDFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_~'
URLSAFE_DISSIMILAR = '23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz-_~'
