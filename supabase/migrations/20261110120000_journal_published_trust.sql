-- Distinguish papers published in a journal without external peer review from peer-reviewed papers.
-- Einstein's 1905 relativity paper was published in Annalen der Physik but was not externally refereed.

alter table published_version
  drop constraint published_version_trust_check,
  add constraint published_version_trust_check
    check (trust in ('peer_reviewed', 'preprint', 'company_reported', 'journal_published'));

alter table source
  drop constraint source_trust_check,
  add constraint source_trust_check
    check (trust in ('peer_reviewed', 'preprint', 'company_reported', 'journal_published'));

alter table moment
  drop constraint moment_trust_check,
  add constraint moment_trust_check
    check (trust in ('peer_reviewed', 'preprint', 'company_reported', 'journal_published'));
