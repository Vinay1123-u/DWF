#pragma once

#include <QString>

class SearchHistory
{
public:
    SearchHistory();
    SearchHistory(int id, int userId, const QString& word, const QString& searchedAt = QString());

    int id() const;
    int userId() const;
    QString word() const;
    QString searchedAt() const;

    void setId(int id);
    void setUserId(int userId);
    void setWord(const QString& word);
    void setSearchedAt(const QString& searchedAt);

private:
    int m_id;
    int m_userId;
    QString m_word;
    QString m_searchedAt;
};
