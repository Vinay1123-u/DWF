#pragma once

#include <QString>

class PasswordHasher
{
public:
    static QString hashPassword(const QString& password);
    static bool verifyPassword(const QString& password, const QString& hash);
};
