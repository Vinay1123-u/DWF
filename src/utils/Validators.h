#pragma once

#include <QString>

class Validators
{
public:
    static bool isValidEmail(const QString& email);
    static bool isStrongPassword(const QString& password);
    static bool isValidUsername(const QString& username);
    static QString trim(const QString& value);
};
