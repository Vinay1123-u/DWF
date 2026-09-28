#pragma once

#include <QObject>
#include <QString>

class User;

class AuthenticationService : public QObject
{
    Q_OBJECT
public:
    explicit AuthenticationService(QObject* parent = nullptr);
    ~AuthenticationService();

    bool registerUser(const QString& username, const QString& email, const QString& password,
                      QString& errorMessage);
    bool loginUser(const QString& email, const QString& password, QString& errorMessage);
    bool logout();
    bool isLoggedIn() const;
    int currentUserId() const;
    QString currentUsername() const;
    QString currentEmail() const;
    void setCurrentUser(int id, const QString& username, const QString& email);
    void clearSession();

signals:
    void userLoggedIn(int userId, const QString& username, const QString& email);
    void userLoggedOut();

private:
    int m_currentUserId;
    QString m_currentUsername;
    QString m_currentEmail;
};
