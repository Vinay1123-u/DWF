#include "database/DatabaseManager.h"

#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QSqlQuery>
#include <QSqlError>
#include <QDateTime>
#include <QVariant>

DatabaseManager::DatabaseManager()
    : m_dbPath(QDir::currentPath() + QDir::separator() + "database" + QDir::separator() + "dictionary.db")
{
    QDir dir(QDir::currentPath() + QDir::separator() + "database");
    if (!dir.exists()) {
        dir.mkpath(".");
    }
}

DatabaseManager::~DatabaseManager()
{
    closeDatabase();
}

bool DatabaseManager::initializeDatabase()
{
    m_database = QSqlDatabase::addDatabase("QSQLITE", "dictionary_connection");
    m_database.setDatabaseName(m_dbPath);

    if (!m_database.open()) {
        return false;
    }

    return createTables();
}

bool DatabaseManager::createTables()
{
    if (!m_database.isOpen()) {
        return false;
    }

    QSqlQuery query(m_database);

    const QString createUsers = R"(
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    )";

    const QString createHistory = R"(
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            word TEXT NOT NULL,
            searched_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    )";

    const QString createSavedWords = R"(
        CREATE TABLE IF NOT EXISTS saved_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            word TEXT NOT NULL,
            saved_at TEXT NOT NULL,
            UNIQUE(user_id, word),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    )";

    if (!query.exec(createUsers)) {
        return false;
    }
    if (!query.exec(createHistory)) {
        return false;
    }
    if (!query.exec(createSavedWords)) {
        return false;
    }

    return true;
}

void DatabaseManager::closeDatabase()
{
    if (m_database.isOpen()) {
        m_database.close();
    }
    m_database = QSqlDatabase();
    QSqlDatabase::removeDatabase("dictionary_connection");
}

bool DatabaseManager::isOpen() const
{
    return m_database.isOpen();
}

QSqlDatabase DatabaseManager::getDatabase()
{
    return m_database;
}

bool DatabaseManager::createUser(const QString& username, const QString& email,
                                const QString& passwordHash, QString& errorMessage)
{
    if (userExistsByEmail(email)) {
        errorMessage = "Email already registered. Please use another email address.";
        return false;
    }

    if (userExistsByUsername(username)) {
        errorMessage = "Username already taken. Please choose another username.";
        return false;
    }

    QSqlQuery query(m_database);
    query.prepare(R"(
        INSERT INTO users (username, email, password_hash, created_at, updated_at)
        VALUES (:username, :email, :password_hash, :created_at, :updated_at)
    )");
    query.bindValue(":username", username);
    query.bindValue(":email", email);
    query.bindValue(":password_hash", passwordHash);
    const QString now = QDateTime::currentDateTimeUtc().toString(Qt::ISODateWithMs);
    query.bindValue(":created_at", now);
    query.bindValue(":updated_at", now);

    if (!query.exec()) {
        errorMessage = "Unable to create your account at this time.";
        return false;
    }

    errorMessage.clear();
    return true;
}

bool DatabaseManager::userExistsByEmail(const QString& email) const
{
    QSqlQuery query(m_database);
    query.prepare("SELECT 1 FROM users WHERE email = :email");
    query.bindValue(":email", email);
    if (!query.exec()) {
        return false;
    }
    return query.next();
}

bool DatabaseManager::userExistsByUsername(const QString& username) const
{
    QSqlQuery query(m_database);
    query.prepare("SELECT 1 FROM users WHERE username = :username");
    query.bindValue(":username", username);
    if (!query.exec()) {
        return false;
    }
    return query.next();
}

QString DatabaseManager::getUserPasswordHash(const QString& email) const
{
    QSqlQuery query(m_database);
    query.prepare("SELECT password_hash FROM users WHERE email = :email");
    query.bindValue(":email", email);
    if (!query.exec() || !query.next()) {
        return QString();
    }
    return query.value(0).toString();
}

QVariantMap DatabaseManager::getUserByEmail(const QString& email) const
{
    QVariantMap result;
    QSqlQuery query(m_database);
    query.prepare("SELECT id, username, email, password_hash, created_at, updated_at FROM users WHERE email = :email");
    query.bindValue(":email", email);
    if (!query.exec() || !query.next()) {
        return result;
    }

    result["id"] = query.value(0).toInt();
    result["username"] = query.value(1).toString();
    result["email"] = query.value(2).toString();
    result["password_hash"] = query.value(3).toString();
    result["created_at"] = query.value(4).toString();
    result["updated_at"] = query.value(5).toString();
    return result;
}

QVariantMap DatabaseManager::getUserById(int userId) const
{
    QVariantMap result;
    QSqlQuery query(m_database);
    query.prepare("SELECT id, username, email, password_hash, created_at, updated_at FROM users WHERE id = :user_id");
    query.bindValue(":user_id", userId);
    if (!query.exec() || !query.next()) {
        return result;
    }

    result["id"] = query.value(0).toInt();
    result["username"] = query.value(1).toString();
    result["email"] = query.value(2).toString();
    result["password_hash"] = query.value(3).toString();
    result["created_at"] = query.value(4).toString();
    result["updated_at"] = query.value(5).toString();
    return result;
}

bool DatabaseManager::addSearchHistory(int userId, const QString& word, QString& errorMessage)
{
    if (word.trimmed().isEmpty()) {
        errorMessage = "Word cannot be empty.";
        return false;
    }

    QSqlQuery query(m_database);
    query.prepare(R"(
        INSERT INTO search_history (user_id, word, searched_at)
        VALUES (:user_id, :word, :searched_at)
    )");
    query.bindValue(":user_id", userId);
    query.bindValue(":word", word.trimmed());
    query.bindValue(":searched_at", QDateTime::currentDateTimeUtc().toString(Qt::ISODateWithMs));

    if (!query.exec()) {
        errorMessage = "Unable to save the search history.";
        return false;
    }

    errorMessage.clear();
    return true;
}

bool DatabaseManager::deleteSearchHistoryItem(int id, int userId)
{
    QSqlQuery query(m_database);
    query.prepare("DELETE FROM search_history WHERE id = :id AND user_id = :user_id");
    query.bindValue(":id", id);
    query.bindValue(":user_id", userId);
    return query.exec();
}

bool DatabaseManager::clearSearchHistory(int userId)
{
    QSqlQuery query(m_database);
    query.prepare("DELETE FROM search_history WHERE user_id = :user_id");
    query.bindValue(":user_id", userId);
    return query.exec();
}

QVariantList DatabaseManager::getSearchHistory(int userId, int limit) const
{
    QVariantList entries;
    QSqlQuery query(m_database);
    query.prepare(R"(
        SELECT id, user_id, word, searched_at
        FROM search_history
        WHERE user_id = :user_id
        ORDER BY searched_at DESC
        LIMIT :limit
    )");
    query.bindValue(":user_id", userId);
    query.bindValue(":limit", limit);
    if (!query.exec()) {
        return entries;
    }

    while (query.next()) {
        QVariantMap item;
        item["id"] = query.value(0).toInt();
        item["user_id"] = query.value(1).toInt();
        item["word"] = query.value(2).toString();
        item["searched_at"] = query.value(3).toString();
        entries.append(item);
    }
    return entries;
}

int DatabaseManager::getSearchHistoryCount(int userId) const
{
    QSqlQuery query(m_database);
    query.prepare("SELECT COUNT(*) FROM search_history WHERE user_id = :user_id");
    query.bindValue(":user_id", userId);
    if (!query.exec() || !query.next()) {
        return 0;
    }
    return query.value(0).toInt();
}

bool DatabaseManager::saveWord(int userId, const QString& word, QString& errorMessage)
{
    if (word.trimmed().isEmpty()) {
        errorMessage = "Word cannot be empty.";
        return false;
    }

    if (isWordSaved(userId, word)) {
        errorMessage = "Word already saved.";
        return false;
    }

    QSqlQuery query(m_database);
    query.prepare(R"(
        INSERT INTO saved_words (user_id, word, saved_at)
        VALUES (:user_id, :word, :saved_at)
    )");
    query.bindValue(":user_id", userId);
    query.bindValue(":word", word.trimmed());
    query.bindValue(":saved_at", QDateTime::currentDateTimeUtc().toString(Qt::ISODateWithMs));

    if (!query.exec()) {
        errorMessage = "Unable to save this word.";
        return false;
    }

    errorMessage.clear();
    return true;
}

bool DatabaseManager::removeSavedWord(int userId, const QString& word)
{
    QSqlQuery query(m_database);
    query.prepare("DELETE FROM saved_words WHERE user_id = :user_id AND word = :word");
    query.bindValue(":user_id", userId);
    query.bindValue(":word", word.trimmed());
    return query.exec();
}

QVariantList DatabaseManager::getSavedWords(int userId) const
{
    QVariantList words;
    QSqlQuery query(m_database);
    query.prepare(R"(
        SELECT id, user_id, word, saved_at
        FROM saved_words
        WHERE user_id = :user_id
        ORDER BY saved_at DESC
    )");
    query.bindValue(":user_id", userId);
    if (!query.exec()) {
        return words;
    }

    while (query.next()) {
        QVariantMap item;
        item["id"] = query.value(0).toInt();
        item["user_id"] = query.value(1).toInt();
        item["word"] = query.value(2).toString();
        item["saved_at"] = query.value(3).toString();
        words.append(item);
    }
    return words;
}

int DatabaseManager::getSavedWordsCount(int userId) const
{
    QSqlQuery query(m_database);
    query.prepare("SELECT COUNT(*) FROM saved_words WHERE user_id = :user_id");
    query.bindValue(":user_id", userId);
    if (!query.exec() || !query.next()) {
        return 0;
    }
    return query.value(0).toInt();
}

bool DatabaseManager::isWordSaved(int userId, const QString& word) const
{
    QSqlQuery query(m_database);
    query.prepare("SELECT 1 FROM saved_words WHERE user_id = :user_id AND word = :word");
    query.bindValue(":user_id", userId);
    query.bindValue(":word", word.trimmed());
    if (!query.exec()) {
        return false;
    }
    return query.next();
}
