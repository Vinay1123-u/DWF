#pragma once

#include <QString>

class SavedWord
{
public:
    SavedWord();
    SavedWord(int id, int userId, const QString& word, const QString& savedAt = QString());

    int id() const;
    int userId() const;
    QString word() const;
    QString savedAt() const;

    void setId(int id);
    void setUserId(int userId);
    void setWord(const QString& word);
    void setSavedAt(const QString& savedAt);

private:
    int m_id;
    int m_userId;
    QString m_word;
    QString m_savedAt;
};
