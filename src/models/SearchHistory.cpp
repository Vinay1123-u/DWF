#include "models/SearchHistory.h"

SearchHistory::SearchHistory() : m_id(-1), m_userId(-1)
{
}

SearchHistory::SearchHistory(int id, int userId, const QString& word, const QString& searchedAt)
    : m_id(id), m_userId(userId), m_word(word), m_searchedAt(searchedAt)
{
}

int SearchHistory::id() const { return m_id; }
int SearchHistory::userId() const { return m_userId; }
QString SearchHistory::word() const { return m_word; }
QString SearchHistory::searchedAt() const { return m_searchedAt; }

void SearchHistory::setId(int id) { m_id = id; }
void SearchHistory::setUserId(int userId) { m_userId = userId; }
void SearchHistory::setWord(const QString& word) { m_word = word; }
void SearchHistory::setSearchedAt(const QString& searchedAt) { m_searchedAt = searchedAt; }
