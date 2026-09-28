#include "utils/Validators.h"

#include <QRegularExpression>

bool Validators::isValidEmail(const QString& email)
{
    static const QRegularExpression emailRegex(QStringLiteral(
        "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"));
    return emailRegex.match(email.trimmed()).hasMatch();
}

bool Validators::isStrongPassword(const QString& password)
{
    return password.length() >= 8;
}

bool Validators::isValidUsername(const QString& username)
{
    const QString trimmed = username.trimmed();
    return !trimmed.isEmpty() && trimmed.length() >= 3;
}

QString Validators::trim(const QString& value)
{
    return value.trimmed();
}
