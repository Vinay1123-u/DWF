#include "models/SavedWord.h"

SavedWord::SavedWord() : m_id(-1), m_userId(-1)
{
}

SavedWord::SavedWord(int id, int userId, const QString& word, const QString& savedAt)
    : m_id(id), m_userId(userId), m_word(word), m_savedAt(savedAt)
{
}

int SavedWord::id() const { return m_id; }
int SavedWord::userId() const { return m_userId; }
QString SavedWord::word() const { return m_word; }
QString SavedWord::savedAt() const { return m_savedAt; }

void SavedWord::setId(int id) { m_id = id; }
void SavedWord::setUserId(int userId) { m_userId = userId; }
void SavedWord::setWord(const QString& word) { m_word = word; }
void SavedWord::setSavedAt(const QString& savedAt) { m_savedAt = savedAt; }
