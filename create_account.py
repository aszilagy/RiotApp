from passlib.hash import sha256_crypt as sha
import argparse
import sys

def main():
    user = sys.argv[1]
    pa = sys.argv[2]
    print(user, pa)

    createPass(user, pa)


def createPass(user, pa):
    username = sha.encrypt(user)
    password = sha.encrypt(pa)

    with (open('pauser.tmp','w')) as fp:
        fp.write('[DEFAULT]\n')
        fp.write(f'USER={user}\n')
        fp.write(f'PASSWORD={pa}\n')
        fp.write(f'USER_ENCRYPT={username}\n')
        fp.write(f'PASSWORD_ENCRYPT={password}')

if __name__ == '__main__':
    main()

