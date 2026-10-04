#include "services/AuthenticationService.h"

#include <QSqlDatabase>
#include <QSqlQuery>
#include <QVariant>

#include "database/DatabaseManager.h"
#include "utils/PasswordHasher.h"
#include "utils/Validators.h"

AuthenticationService::AuthenticationService(QObject* parent)
    : QObject(parent), m_currentUserId(-1)
{
}

AuthenticationService::~AuthenticationService() = default;

bool AuthenticationService::registerUser(const QString& username, const QString& email,
                                         const QString& password, QString& errorMessage)
{
    const QString trimmedUsername = Validators::trim(username);
    const QString trimmedEmail = Validators::trim(email).toLower();
    const QString trimmedPassword = password;

    if (!Validators::isValidUsername(trimmedUsername)) {
        errorMessage = "Username is required.";
        return false;
    }
    if (trimmedEmail.isEmpty() || !Validators::isValidEmail(trimmedEmail)) {
        errorMessage = "Please enter a valid email address.";
        return false;
    }
    if (!Validators::isStrongPassword(trimmedPassword)) {
        errorMessage = "Password must be at least 8 characters long.";
        return false;
    }

    DatabaseManager db;
    if (!db.initializeDatabase()) {
        errorMessage = "Unable to initialize the database.";
        return false;
    }

    if (db.userExistsByEmail(trimmedEmail)) {
        errorMessage = "Email already registered. Please use another email address.";
        return false;
    }
    if (db.userExistsByUsername(trimmedUsername)) {
        errorMessage = "Username already taken. Please choose another username.";
        return false;
    }

    const QString hash = PasswordHasher::hashPassword(trimmedPassword);
    return db.createUser(trimmedUsername, trimmedEmail, hash, errorMessage);
}

bool AuthenticationService::loginUser(const QString& email, const QString& password, QString& errorMessage)
{
    const QString trimmedEmail = Validators::trim(email).toLower();
    DatabaseManager db;
    if (!db.initializeDatabase()) {
        errorMessage = "Unable to access the database.";
        return false;
    }

    QVariantMap user = db.getUserByEmail(trimmedEmail);
    if (user.isEmpty() || !user.contains("password_hash")) {
        errorMessage = "Invalid email or password.";
        return false;
    }

    const QString storedHash = user["password_hash"].toString();
    if (!PasswordHasher::verifyPassword(password, storedHash)) {
        errorMessage = "Invalid email or password.";
        return false;
    }

    m_currentUserId = user["id"].toInt();
    m_currentUsername = user["username"].toString();
    m_currentEmail = user["email"].toString();

    emit userLoggedIn(m_currentUserId, m_currentUsername, m_currentEmail);
    errorMessage.clear();
    return true;
}

bool AuthenticationService::logout()
{
    clearSession();
    emit userLoggedOut();
    return true;
}

bool AuthenticationService::isLoggedIn() const
{
    return m_currentUserId > 0;
}

int AuthenticationService::currentUserId() const
{
    return m_currentUserId;
}

QString AuthenticationService::currentUsername() const
{
    return m_currentUsername;
}

QString AuthenticationService::currentEmail() const
{
    return m_currentEmail;
}

void AuthenticationService::setCurrentUser(int id, const QString& username, const QString& email)
{
    m_currentUserId = id;
    m_currentUsername = username;
    m_currentEmail = email;
    if (id > 0) {
        emit userLoggedIn(id, username, email);
    }
}

void AuthenticationService::clearSession()
{
    m_currentUserId = -1;
    m_currentUsername.clear();
    m_currentEmail.clear();
}
