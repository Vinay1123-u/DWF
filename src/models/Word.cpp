#include "models/Word.h"

#include <QJsonArray>
#include <QJsonValue>

namespace {
QStringList jsonArrayToStringList(const QJsonValue& value)
{
    QStringList result;
    if (!value.isArray()) {
        return result;
    }
    for (const QJsonValue& item : value.toArray()) {
        if (item.isString()) {
            result << item.toString();
        }
    }
    return result;
}
}

Word::Word() : m_word(""), m_pronunciation(""), m_partOfSpeech("")
{
}

Word::Word(const QString& word, const QString& pronunciation,
           const QString& partOfSpeech, const QStringList& definitions,
           const QStringList& synonyms, const QStringList& antonyms,
           const QStringList& examples, const QStringList& relatedWords)
    : m_word(word), m_pronunciation(pronunciation), m_partOfSpeech(partOfSpeech),
      m_definitions(definitions), m_synonyms(synonyms), m_antonyms(antonyms),
      m_examples(examples), m_relatedWords(relatedWords)
{
}

QString Word::word() const { return m_word; }
QString Word::pronunciation() const { return m_pronunciation; }
QString Word::partOfSpeech() const { return m_partOfSpeech; }
QStringList Word::definitions() const { return m_definitions; }
QStringList Word::synonyms() const { return m_synonyms; }
QStringList Word::antonyms() const { return m_antonyms; }
QStringList Word::examples() const { return m_examples; }
QStringList Word::relatedWords() const { return m_relatedWords; }

void Word::setWord(const QString& word) { m_word = word; }
void Word::setPronunciation(const QString& pronunciation) { m_pronunciation = pronunciation; }
void Word::setPartOfSpeech(const QString& partOfSpeech) { m_partOfSpeech = partOfSpeech; }
void Word::setDefinitions(const QStringList& definitions) { m_definitions = definitions; }
void Word::setSynonyms(const QStringList& synonyms) { m_synonyms = synonyms; }
void Word::setAntonyms(const QStringList& antonyms) { m_antonyms = antonyms; }
void Word::setExamples(const QStringList& examples) { m_examples = examples; }
void Word::setRelatedWords(const QStringList& relatedWords) { m_relatedWords = relatedWords; }

bool Word::isValid() const
{
    return !m_word.trimmed().isEmpty() || !m_definitions.isEmpty() || !m_examples.isEmpty();
}

QJsonObject Word::toJsonObject() const
{
    QJsonObject object;
    object["word"] = m_word;
    object["pronunciation"] = m_pronunciation;
    object["part_of_speech"] = m_partOfSpeech;
    object["definitions"] = QJsonArray::fromStringList(m_definitions);
    object["synonyms"] = QJsonArray::fromStringList(m_synonyms);
    object["antonyms"] = QJsonArray::fromStringList(m_antonyms);
    object["examples"] = QJsonArray::fromStringList(m_examples);
    object["related_words"] = QJsonArray::fromStringList(m_relatedWords);
    return object;
}

Word Word::fromJsonObject(const QJsonObject& object)
{
    Word word;
    word.setWord(object.value("word").toString());
    word.setPronunciation(object.value("pronunciation").toString());
    word.setPartOfSpeech(object.value("part_of_speech").toString());

    word.setDefinitions(jsonArrayToStringList(object.value("definitions")));
    word.setSynonyms(jsonArrayToStringList(object.value("synonyms")));
    word.setAntonyms(jsonArrayToStringList(object.value("antonyms")));
    word.setExamples(jsonArrayToStringList(object.value("examples")));
    word.setRelatedWords(jsonArrayToStringList(object.value("related_words")));
    return word;
}
