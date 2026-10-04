#pragma once

#include <QSqlDatabase>
#include <QSqlQuery>
#include <QSqlError>
#include <QStringList>
#include <QVariant>

class DatabaseManager
{
public:
    DatabaseManager();
    ~DatabaseManager();

    bool initializeDatabase();
    bool createTables();
    void closeDatabase();
    bool isOpen() const;
    QSqlDatabase getDatabase();

    bool createUser(const QString& username, const QString& email, const QString& passwordHash,
                    QString& errorMessage);
    bool userExistsByEmail(const QString& email) const;
    bool userExistsByUsername(const QString& username) const;
    QString getUserPasswordHash(const QString& email) const;
    QVariantMap getUserByEmail(const QString& email) const;
    QVariantMap getUserById(int userId) const;

    bool addSearchHistory(int userId, const QString& word, QString& errorMessage);
    bool deleteSearchHistoryItem(int id, int userId);
    bool clearSearchHistory(int userId);
    QVariantList getSearchHistory(int userId, int limit = 20) const;
    int getSearchHistoryCount(int userId) const;

    bool saveWord(int userId, const QString& word, QString& errorMessage);
    bool removeSavedWord(int userId, const QString& word);
    QVariantList getSavedWords(int userId) const;
    int getSavedWordsCount(int userId) const;
    bool isWordSaved(int userId, const QString& word) const;

private:
    QSqlDatabase m_database;
    QString m_dbPath;
    QString m_connectionName;
};
