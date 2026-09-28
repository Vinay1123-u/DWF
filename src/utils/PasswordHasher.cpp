#include "utils/PasswordHasher.h"

#include <QCryptographicHash>
#include <QByteArray>

QString PasswordHasher::hashPassword(const QString& password)
{
    return QString::fromLatin1(QCryptographicHash::hash(password.toUtf8(), QCryptographicHash::Sha256).toHex());
}

bool PasswordHasher::verifyPassword(const QString& password, const QString& hash)
{
    return hashPassword(password) == hash;
}
