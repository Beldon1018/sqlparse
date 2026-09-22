import pytest

import sqlparse
from sqlparse.exceptions import SQLParseError


class TestFormat:
    def test_keywordcase(self):
        sql = 'select * from bar; -- select foo\n'
        res = sqlparse.format(sql, keyword_case='upper')
        assert res == 'SELECT * FROM bar; -- select foo\n'
        res = sqlparse.format(sql, keyword_case='capitalize')
        assert res == 'Select * From bar; -- select foo\n'
        res = sqlparse.format(sql.upper(), keyword_case='lower')
        assert res == 'select * from BAR; -- SELECT FOO\n'

    def test_keywordcase_invalid_option(self):
        sql = 'select * from bar; -- select foo\n'
        with pytest.raises(SQLParseError):
            sqlparse.format(sql, keyword_case='foo')

    def test_identifiercase(self):
        sql = 'select * from bar; -- select foo\n'
        res = sqlparse.format(sql, identifier_case='upper')
        assert res == 'select * from BAR; -- select foo\n'
        res = sqlparse.format(sql, identifier_case='capitalize')
        assert res == 'select * from Bar; -- select foo\n'
        res = sqlparse.format(sql.upper(), identifier_case='lower')
        assert res == 'SELECT * FROM bar; -- SELECT FOO\n'

    def test_identifiercase_invalid_option(self):
        sql = 'select * from bar; -- select foo\n'
        with pytest.raises(SQLParseError):
            sqlparse.format(sql, identifier_case='foo')

    def test_identifiercase_quotes(self):
        sql = 'select * from "foo"."bar"'
        res = sqlparse.format(sql, identifier_case="upper")
        assert res == 'select * from "foo"."bar"'

    def test_strip_comments_single(self):
        sql = 'select *-- statement starts here\nfrom foo'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == 'select *\nfrom foo'
        sql = 'select * -- statement starts here\nfrom foo'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == 'select *\nfrom foo'
        sql = 'select-- foo\nfrom -- bar\nwhere'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == 'select\nfrom\nwhere'
        sql = 'select *-- statement starts here\n\nfrom foo'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == 'select *\n\nfrom foo'
        sql = 'select * from foo-- statement starts here\nwhere'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == 'select * from foo\nwhere'
        sql = 'select a-- statement starts here\nfrom foo'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == 'select a\nfrom foo'
        sql = '--comment\nselect a-- statement starts here\n' \
              'from foo--comment\nf'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == 'select a\nfrom foo\nf'
        sql = '--A;--B;'
        res = ''
        assert res == sqlparse.format(sql, strip_comments=True)
        sql = '--A;\n--B;'
        res = ''
        assert res == sqlparse.format(sql, strip_comments=True)

    def test_strip_comments_invalid_option(self):
        sql = 'select-- foo\nfrom -- bar\nwhere'
        with pytest.raises(SQLParseError):
            sqlparse.format(sql, strip_comments=None)

    def test_strip_comments_multi(self):
        sql = '/* sql starts here */\nselect'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == 'select'
        sql = '/* sql starts here */ select'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == ' select'  # note whitespace is preserved, see issue 772
        sql = '/*\n * sql starts here\n */\nselect'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == 'select'
        sql = '/* sql starts here */'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == ''
        sql = '/* sql starts here */\n/* or here */'
        res = sqlparse.format(sql, strip_comments=True, strip_whitespace=True)
        assert res == ''
        sql = 'select (/* sql starts here */ select 2)'
        res = sqlparse.format(sql, strip_comments=True, strip_whitespace=True)
        assert res == 'select (select 2)'
        sql = 'select (/* sql /* starts here */ select 2)'
        res = sqlparse.format(sql, strip_comments=True, strip_whitespace=True)
        assert res == 'select (select 2)'

    def test_strip_comments_preserves_linebreak(self):
        sql = 'select * -- a comment\r\nfrom foo'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == 'select *\nfrom foo'
        sql = 'select * -- a comment\nfrom foo'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == 'select *\nfrom foo'
        sql = 'select * -- a comment\rfrom foo'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == 'select *\nfrom foo'
        sql = 'select * -- a comment\r\n\r\nfrom foo'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == 'select *\n\nfrom foo'
        sql = 'select * -- a comment\n\nfrom foo'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == 'select *\n\nfrom foo'

    def test_strip_comments_preserves_whitespace(self):
        sql = 'SELECT 1/*bar*/ AS foo'  # see issue772
        res = sqlparse.format(sql, strip_comments=True)
        assert res == 'SELECT 1 AS foo'

    def test_strip_comments_preserves_hint(self):
        sql = 'select --+full(u)'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == sql
        sql = '#+ hint\nselect * from foo'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == sql
        sql = 'select --+full(u)\n--comment simple'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == 'select --+full(u)\n'
        sql = '#+ hint\nselect * from foo\n# comment simple'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == '#+ hint\nselect * from foo\n'
        sql = 'SELECT /*+cluster(T)*/* FROM T_EEE T where A >:1'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == sql
        sql = 'insert /*+ DIRECT */ into sch.table_name as select * from foo'
        res = sqlparse.format(sql, strip_comments=True)
        assert res == sql

    def test_strip_ws(self):
        f = lambda sql: sqlparse.format(sql, strip_whitespace=True)
        s = 'select\n* from      foo\n\twhere  ( 1 = 2 )\n'
        assert f(s) == 'select * from foo where (1 = 2)'
        s = 'select -- foo\nfrom    bar\n'
        assert f(s) == 'select -- foo\nfrom bar'

    @pytest.mark.parametrize('sql', [
        '( AS )',
        '(( AS ))',
        'f( AS )',
        'SELECT ( AS ) FROM t',
        'SELECT * FROM t WHERE x IN ( AS )',
        'SELECT (SELECT ( AS ) FROM u) FROM t',
        'SELECT (a, ( AS )) FROM t',
    ])
    @pytest.mark.parametrize('options', [
        {},
        {'strip_whitespace': True},
        {'reindent': True},
        {'reindent_aligned': True},
        {'keyword_case': 'upper'},
        {'keyword_case': 'lower'},
        {'strip_whitespace': True, 'keyword_case': 'capitalize'},
        {'strip_whitespace': True, 'reindent_aligned': True,
         'keyword_case': 'upper'},
    ])
    def test_degenerate_parenthesis_no_crash(self, sql, options):
        # Degenerate parenthesis groups must not raise IndexError,
        # regardless of the combination of formatting options.
        res = sqlparse.format(sql, **options)
        assert isinstance(res, str)

    def test_strip_ws_parenthesis_unchanged(self):
        # Normal parenthesis groups keep their existing results.
        f = lambda sql: sqlparse.format(sql, strip_whitespace=True)
        assert f('SELECT ( a ) FROM t') == 'SELECT (a) FROM t'
        assert f('SELECT (  ) FROM t') == 'SELECT () FROM t'
        assert f('SELECT (a, b) FROM t') == 'SELECT (a, b) FROM t'

    def test_strip_ws_invalid_option(self):
        s = 'select -- foo\nfrom    bar\n'
        with pytest.raises(SQLParseError):
            sqlparse.format(s, strip_whitespace=None)

    def test_preserve_ws(self):
        # preserve at least one whitespace after subgroups
        f = lambda sql: sqlparse.format(sql, strip_whitespace=True)
        s = 'select\n* /* foo */  from bar '
        assert f(s) == 'select * /* foo */ from bar'

    def test_notransform_of_quoted_crlf(self):
        # Make sure that CR/CR+LF characters inside string literals don't get
        # affected by the formatter.

        s1 = "SELECT some_column LIKE 'value\r'"
        s2 = "SELECT some_column LIKE 'value\r'\r\nWHERE id = 1\n"
        s3 = "SELECT some_column LIKE 'value\\'\r' WHERE id = 1\r"
        s4 = "SELECT some_column LIKE 'value\\\\\\'\r' WHERE id = 1\r\n"

        f = lambda x: sqlparse.format(x)

        # Because of the use of
        assert f(s1) == "SELECT some_column LIKE 'value\r'"
        assert f(s2) == "SELECT some_column LIKE 'value\r'\nWHERE id = 1\n"
        assert f(s3) == "SELECT some_column LIKE 'value\\'\r' WHERE id = 1\n"
        assert (f(s4)
                == "SELECT some_column LIKE 'value\\\\\\'\r' WHERE id = 1\n")


class TestFormatReindentAligned:
    @staticmethod
    def formatter(sql):
        return sqlparse.format(sql, reindent_aligned=True)

    def test_basic(self):
        sql = """
            select a, b as bb,c from table
            join (select a * 2 as a from new_table) other
            on table.a = other.a
            where c is true
            and b between 3 and 4
            or d is 'blue'
            limit 10
            """

        assert self.formatter(sql) == '\n'.join([
            'select a,',
            '       b as bb,',
            '       c',
            '  from table',
            '  join (',
            '        select a * 2 as a',
            '          from new_table',
            '       ) other',
            '    on table.a = other.a',
            ' where c is true',
            '   and b between 3 and 4',
            "    or d is 'blue'",
            ' limit 10'])

    def test_joins(self):
        sql = """
            select * from a
            join b on a.one = b.one
            left join c on c.two = a.two and c.three = a.three
            full outer join d on d.three = a.three
            cross join e on e.four = a.four
            join f using (one, two, three)
            """
        assert self.formatter(sql) == '\n'.join([
            'select *',
            '  from a',
            '  join b',
            '    on a.one = b.one',
            '  left join c',
            '    on c.two = a.two',
            '   and c.three = a.three',
            '  full outer join d',
            '    on d.three = a.three',
            ' cross join e',
            '    on e.four = a.four',
            '  join f using (one, two, three)'])

    def test_case_statement(self):
        sql = """
            select a,
            case when a = 0
            then 1
            when bb = 1 then 1
            when c = 2 then 2
            else 0 end as d,
            extra_col
            from table
            where c is true
            and b between 3 and 4
            """
        assert self.formatter(sql) == '\n'.join([
            'select a,',
            '       case when a = 0  then 1',
            '            when bb = 1 then 1',
            '            when c = 2  then 2',
            '            else 0',
            '             end as d,',
            '       extra_col',
            '  from table',
            ' where c is true',
            '   and b between 3 and 4'])

    def test_case_statement_with_between(self):
        sql = """
            select a,
            case when a = 0
            then 1
            when bb = 1 then 1
            when c = 2 then 2
            when d between 3 and 5 then 3
            else 0 end as d,
            extra_col
            from table
            where c is true
            and b between 3 and 4
            """
        assert self.formatter(sql) == '\n'.join([
            'select a,',
            '       case when a = 0             then 1',
            '            when bb = 1            then 1',
            '            when c = 2             then 2',
            '            when d between 3 and 5 then 3',
            '            else 0',
            '             end as d,',
            '       extra_col',
            '  from table',
            ' where c is true',
            '   and b between 3 and 4'])

    def test_group_by(self):
        sql = """
            select a, b, c, sum(x) as sum_x, count(y) as cnt_y
            from table
            group by a,b,c
            having sum(x) > 1
            and count(y) > 5
            order by 3,2,1
            """
        assert self.formatter(sql) == '\n'.join([
            'select a,',
            '       b,',
            '       c,',
            '       sum(x) as sum_x,',
            '       count(y) as cnt_y',
            '  from table',
            ' group by a,',
            '          b,',
            '          c',
            'having sum(x) > 1',
            '   and count(y) > 5',
            ' order by 3,',
            '          2,',
            '          1'])

    def test_group_by_subquery(self):
        # TODO: add subquery alias when test_identifier_list_subquery fixed
        sql = """
            select *, sum_b + 2 as mod_sum
            from (
              select a, sum(b) as sum_b
              from table
              group by a,z)
            order by 1,2
            """
        assert self.formatter(sql) == '\n'.join([
            'select *,',
            '       sum_b + 2 as mod_sum',
            '  from (',
            '        select a,',
            '               sum(b) as sum_b',
            '          from table',
            '         group by a,',
            '                  z',
            '       )',
            ' order by 1,',
            '          2'])

    def test_window_functions(self):
        sql = """
            select a,
            SUM(a) OVER (PARTITION BY b ORDER BY c ROWS
            BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as sum_a,
            ROW_NUMBER() OVER
            (PARTITION BY b, c ORDER BY d DESC) as row_num
            from table"""
        assert self.formatter(sql) == '\n'.join([
            'select a,',
            '       SUM(a) OVER (PARTITION BY b ORDER BY c ROWS '
            'BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as sum_a,',
            '       ROW_NUMBER() OVER '
            '(PARTITION BY b, c ORDER BY d DESC) as row_num',
            '  from table'])

    @pytest.mark.parametrize('sql', [
        "CASE 'a' := WHERE END SELECT GO # ->>",
        'SELECT CASE WHEN a THEN b FROM t',
        'SELECT CASE END FROM t',
        'CASE',
        'CASE WHEN',
        'SELECT CASE WHEN a THEN b ELSE END FROM t',
        'SELECT CASE WHEN a THEN CASE WHEN b THEN c END END FROM t',
        'SELECT * FROM t WHERE x IN (SELECT CASE WHEN a THEN b END FROM u)',
    ])
    @pytest.mark.parametrize('options', [
        {'reindent_aligned': True},
        {'reindent_aligned': True, 'keyword_case': 'upper'},
        {'reindent_aligned': True, 'strip_whitespace': True},
    ])
    def test_malformed_case_no_crash(self, sql, options):
        # Malformed CASE constructs must not raise ValueError.
        res = sqlparse.format(sql, **options)
        assert isinstance(res, str)

    def test_case_statement_else_end_unchanged(self):
        sql = 'SELECT CASE WHEN a THEN b ELSE c END FROM t'
        assert self.formatter(sql) == (
            'SELECT CASE WHEN a THEN b\n'
            '            ELSE c\n'
            '             END\n'
            '  FROM t')

    @pytest.mark.parametrize('clause', [
        'OFFSET 0 ROWS FETCH NEXT 100 ROWS ONLY',
        'OFFSET 0 ROWS FETCH FIRST 100 ROWS ONLY',
        'OFFSET 0 ROWS FETCH FIRST 100 ROW ONLY',
        'OFFSET 0 ROWS FETCH NEXT 100 ROWS ONLY',
    ])
    def test_offset_fetch_clause(self, clause):
        sql = ('SELECT id FROM tbl WHERE id > 0 '
               f'ORDER BY id ASC {clause}')
        res = self.formatter(sql)
        # the whole paging clause stays on a single unindented line
        assert f'\n{clause}\n' in f'\n{res}\n'
        # ONLY must never be orphaned on its own line
        for line in res.splitlines():
            assert not line.strip().startswith('ONLY')

    def test_offset_without_fetch(self):
        res = self.formatter('SELECT a FROM t ORDER BY a OFFSET 5 ROWS')
        assert '\nOFFSET 5 ROWS' in f'\n{res}'

    @pytest.mark.parametrize('sql,fragment', [
        ('ALTER TABLE t ADD CONSTRAINT c1 PRIMARY KEY (a, b)',
         'ADD CONSTRAINT'),
        ('ALTER TABLE t ADD FOREIGN KEY (a) REFERENCES u(b)',
         'ADD FOREIGN KEY'),
        ('SELECT a FROM t WHERE jdoc IS JSON', 'IS JSON'),
    ])
    def test_keyword_substrings_not_split(self, sql, fragment):
        # Keywords that merely contain a shorter clause keyword as a
        # substring (CONSTRAINT/ONLY/JSON contain "ON", FOREIGN contains
        # "OR") must not start a new clause line.
        res = self.formatter(sql)
        assert any(fragment in line for line in res.splitlines())

    def test_join_on_alignment_unchanged(self):
        res = self.formatter(
            'SELECT a FROM t1 JOIN t2 ON t1.a = t2.a WHERE t1.b > 1')
        assert '\n  JOIN t2' in res
        assert '\n    ON t1.a = t2.a' in res

    def test_limit_unchanged(self):
        res = self.formatter('SELECT id FROM tbl ORDER BY id LIMIT 10')
        assert '\n LIMIT 10' in res

    def test_between_and_unchanged(self):
        res = self.formatter('SELECT a FROM t WHERE a BETWEEN 1 AND 5')
        assert '\n WHERE a BETWEEN 1 AND 5' in res


class TestSpacesAroundOperators:
    @staticmethod
    def formatter(sql):
        return sqlparse.format(sql, use_space_around_operators=True)

    def test_basic(self):
        sql = ('select a+b as d from table '
               'where (c-d)%2= 1 and e> 3.0/4 and z^2 <100')
        assert self.formatter(sql) == (
            'select a + b as d from table '
            'where (c - d) % 2 = 1 and e > 3.0 / 4 and z ^ 2 < 100')

    def test_bools(self):
        sql = 'select * from table where a &&b or c||d'
        assert self.formatter(
            sql) == 'select * from table where a && b or c || d'

    def test_nested(self):
        sql = 'select *, case when a-b then c end from table'
        assert self.formatter(
            sql) == 'select *, case when a - b then c end from table'

    def test_wildcard_vs_mult(self):
        sql = 'select a*b-c from table'
        assert self.formatter(sql) == 'select a * b - c from table'


class TestFormatReindent:
    def test_option(self):
        with pytest.raises(SQLParseError):
            sqlparse.format('foo', reindent=2)
        with pytest.raises(SQLParseError):
            sqlparse.format('foo', indent_tabs=2)
        with pytest.raises(SQLParseError):
            sqlparse.format('foo', reindent=True, indent_width='foo')
        with pytest.raises(SQLParseError):
            sqlparse.format('foo', reindent=True, indent_width=-12)
        with pytest.raises(SQLParseError):
            sqlparse.format('foo', reindent=True, wrap_after='foo')
        with pytest.raises(SQLParseError):
            sqlparse.format('foo', reindent=True, wrap_after=-12)
        with pytest.raises(SQLParseError):
            sqlparse.format('foo', reindent=True, comma_first='foo')

    def test_stmts(self):
        f = lambda sql: sqlparse.format(sql, reindent=True)
        s = 'select foo; select bar'
        assert f(s) == 'select foo;\n\nselect bar'
        s = 'select foo'
        assert f(s) == 'select foo'
        s = 'select foo; -- test\n select bar'
        assert f(s) == 'select foo; -- test\n\nselect bar'

    def test_keywords(self):
        f = lambda sql: sqlparse.format(sql, reindent=True)
        s = 'select * from foo union select * from bar;'
        assert f(s) == '\n'.join([
            'select *',
            'from foo',
            'union',
            'select *',
            'from bar;'])

    def test_keywords_between(self):
        # issue 14
        # don't break AND after BETWEEN
        f = lambda sql: sqlparse.format(sql, reindent=True)
        s = 'and foo between 1 and 2 and bar = 3'
        assert f(s) == '\n'.join([
            '',
            'and foo between 1 and 2',
            'and bar = 3'])

    def test_parenthesis(self):
        f = lambda sql: sqlparse.format(sql, reindent=True)
        s = 'select count(*) from (select * from foo);'
        assert f(s) == '\n'.join([
            'select count(*)',
            'from',
            '  (select *',
            '   from foo);'])
        assert f("select f(1)") == 'select f(1)'
        assert f("select f( 1 )") == 'select f(1)'
        assert f("select f(\n\n\n1\n\n\n)") == 'select f(1)'
        assert f("select f(\n\n\n 1 \n\n\n)") == 'select f(1)'
        assert f("select f(\n\n\n  1  \n\n\n)") == 'select f(1)'

    def test_where(self):
        f = lambda sql: sqlparse.format(sql, reindent=True)
        s = 'select * from foo where bar = 1 and baz = 2 or bzz = 3;'
        assert f(s) == '\n'.join([
            'select *',
            'from foo',
            'where bar = 1',
            '  and baz = 2',
            '  or bzz = 3;'])

        s = 'select * from foo where bar = 1 and (baz = 2 or bzz = 3);'
        assert f(s) == '\n'.join([
            'select *',
            'from foo',
            'where bar = 1',
            '  and (baz = 2',
            '       or bzz = 3);'])

    def test_join(self):
        f = lambda sql: sqlparse.format(sql, reindent=True)
        s = 'select * from foo join bar on 1 = 2'
        assert f(s) == '\n'.join([
            'select *',
            'from foo',
            'join bar on 1 = 2'])
        s = 'select * from foo inner join bar on 1 = 2'
        assert f(s) == '\n'.join([
            'select *',
            'from foo',
            'inner join bar on 1 = 2'])
        s = 'select * from foo left outer join bar on 1 = 2'
        assert f(s) == '\n'.join([
            'select *',
            'from foo',
            'left outer join bar on 1 = 2'])
        s = 'select * from foo straight_join bar on 1 = 2'
        assert f(s) == '\n'.join([
            'select *',
            'from foo',
            'straight_join bar on 1 = 2'])

    def test_identifier_list(self):
        f = lambda sql: sqlparse.format(sql, reindent=True)
        s = 'select foo, bar, baz from table1, table2 where 1 = 2'
        assert f(s) == '\n'.join([
            'select foo,',
            '       bar,',
            '       baz',
            'from table1,',
            '     table2',
            'where 1 = 2'])
        s = 'select a.*, b.id from a, b'
        assert f(s) == '\n'.join([
            'select a.*,',
            '       b.id',
            'from a,',
            '     b'])

    def test_identifier_list_with_wrap_after(self):
        f = lambda sql: sqlparse.format(sql, reindent=True, wrap_after=14)
        s = 'select foo, bar, baz from table1, table2 where 1 = 2'
        assert f(s) == '\n'.join([
            'select foo, bar,',
            '       baz',
            'from table1, table2',
            'where 1 = 2'])

    def test_identifier_list_comment_first(self):
        f = lambda sql: sqlparse.format(sql, reindent=True, comma_first=True)
        # not the 3: It cleans up whitespace too!
        s = 'select foo, bar, baz from table where foo in (1, 2,3)'
        assert f(s) == '\n'.join([
            'select foo',
            '     , bar',
            '     , baz',
            'from table',
            'where foo in (1',
            '            , 2',
            '            , 3)'])

    def test_identifier_list_with_functions(self):
        f = lambda sql: sqlparse.format(sql, reindent=True)
        s = ("select 'abc' as foo, coalesce(col1, col2)||col3 as bar,"
             "col3 from my_table")
        assert f(s) == '\n'.join([
            "select 'abc' as foo,",
            "       coalesce(col1, col2)||col3 as bar,",
            "       col3",
            "from my_table"])

    def test_long_identifier_list_with_functions(self):
        f = lambda sql: sqlparse.format(sql, reindent=True, wrap_after=30)
        s = ("select 'abc' as foo, json_build_object('a',  a,"
             "'b', b, 'c', c, 'd', d, 'e', e) as col2"
             "col3 from my_table")
        assert f(s) == '\n'.join([
            "select 'abc' as foo,",
            "       json_build_object('a',",
            "         a, 'b', b, 'c', c, 'd', d,",
            "         'e', e) as col2col3",
            "from my_table"])

    def test_case(self):
        f = lambda sql: sqlparse.format(sql, reindent=True)
        s = 'case when foo = 1 then 2 when foo = 3 then 4 else 5 end'
        assert f(s) == '\n'.join([
            'case',
            '    when foo = 1 then 2',
            '    when foo = 3 then 4',
            '    else 5',
            'end'])

    def test_case2(self):
        f = lambda sql: sqlparse.format(sql, reindent=True)
        s = 'case(foo) when bar = 1 then 2 else 3 end'
        assert f(s) == '\n'.join([
            'case(foo)',
            '    when bar = 1 then 2',
            '    else 3',
            'end'])

    def test_nested_identifier_list(self):
        # issue4
        f = lambda sql: sqlparse.format(sql, reindent=True)
        s = '(foo as bar, bar1, bar2 as bar3, b4 as b5)'
        assert f(s) == '\n'.join([
            '(foo as bar,',
            ' bar1,',
            ' bar2 as bar3,',
            ' b4 as b5)'])

    def test_duplicate_linebreaks(self):
        # issue3
        f = lambda sql: sqlparse.format(sql, reindent=True)
        s = 'select c1 -- column1\nfrom foo'
        assert f(s) == '\n'.join([
            'select c1 -- column1',
            'from foo'])
        s = 'select c1 -- column1\nfrom foo'
        r = sqlparse.format(s, reindent=True, strip_comments=True)
        assert r == '\n'.join([
            'select c1',
            'from foo'])
        s = 'select c1\nfrom foo\norder by c1'
        assert f(s) == '\n'.join([
            'select c1',
            'from foo',
            'order by c1'])
        s = 'select c1 from t1 where (c1 = 1) order by c1'
        assert f(s) == '\n'.join([
            'select c1',
            'from t1',
            'where (c1 = 1)',
            'order by c1'])

    def test_keywordfunctions(self):
        # issue36
        f = lambda sql: sqlparse.format(sql, reindent=True)
        s = 'select max(a) b, foo, bar'
        assert f(s) == '\n'.join([
            'select max(a) b,',
            '       foo,',
            '       bar'])

    def test_identifier_and_functions(self):
        # issue45
        f = lambda sql: sqlparse.format(sql, reindent=True)
        s = 'select foo.bar, nvl(1) from dual'
        assert f(s) == '\n'.join([
            'select foo.bar,',
            '       nvl(1)',
            'from dual'])

    def test_insert_values(self):
        # issue 329
        f = lambda sql: sqlparse.format(sql, reindent=True)
        s = 'insert into foo values (1, 2)'
        assert f(s) == '\n'.join([
            'insert into foo',
            'values (1, 2)'])

        s = 'insert into foo values (1, 2), (3, 4), (5, 6)'
        assert f(s) == '\n'.join([
            'insert into foo',
            'values (1, 2),',
            '       (3, 4),',
            '       (5, 6)'])

        s = 'insert into foo(a, b) values (1, 2), (3, 4), (5, 6)'
        assert f(s) == '\n'.join([
            'insert into foo(a, b)',
            'values (1, 2),',
            '       (3, 4),',
            '       (5, 6)'])

        f = lambda sql: sqlparse.format(sql, reindent=True,
                                        comma_first=True)
        s = 'insert into foo values (1, 2)'
        assert f(s) == '\n'.join([
            'insert into foo',
            'values (1, 2)'])

        s = 'insert into foo values (1, 2), (3, 4), (5, 6)'
        assert f(s) == '\n'.join([
            'insert into foo',
            'values (1, 2)',
            '     , (3, 4)',
            '     , (5, 6)'])

        s = 'insert into foo(a, b) values (1, 2), (3, 4), (5, 6)'
        assert f(s) == '\n'.join([
            'insert into foo(a, b)',
            'values (1, 2)',
            '     , (3, 4)',
            '     , (5, 6)'])


class TestOutputFormat:
    def test_python(self):
        sql = 'select * from foo;'
        f = lambda sql: sqlparse.format(sql, output_format='python')
        assert f(sql) == "sql = 'select * from foo;'"
        f = lambda sql: sqlparse.format(sql, output_format='python',
                                        reindent=True)
        assert f(sql) == '\n'.join([
            "sql = ('select * '",
            "       'from foo;')"])

    def test_python_multiple_statements(self):
        sql = 'select * from foo; select 1 from dual'
        f = lambda sql: sqlparse.format(sql, output_format='python')
        assert f(sql) == '\n'.join([
            "sql = 'select * from foo; '",
            "sql2 = 'select 1 from dual'"])

    @pytest.mark.xfail(reason="Needs fixing")
    def test_python_multiple_statements_with_formatting(self):
        sql = 'select * from foo; select 1 from dual'
        f = lambda sql: sqlparse.format(sql, output_format='python',
                                        reindent=True)
        assert f(sql) == '\n'.join([
            "sql = ('select * '",
            "       'from foo;')",
            "sql2 = ('select 1 '",
            "        'from dual')"])

    def test_php(self):
        sql = 'select * from foo;'
        f = lambda sql: sqlparse.format(sql, output_format='php')
        assert f(sql) == '$sql = "select * from foo;";'
        f = lambda sql: sqlparse.format(sql, output_format='php',
                                        reindent=True)
        assert f(sql) == '\n'.join([
            '$sql  = "select * ";',
            '$sql .= "from foo;";'])

    def test_python_escapes_backslashes(self):
        # GHSA-3496-9g83-7v6x: backslashes must be escaped before quotes so
        # crafted SQL cannot break out of the generated Python string literal.
        # SQL  select '\foo\'  -> each \ doubled, each ' escaped.
        sql = "select '\\foo\\'"
        f = lambda sql: sqlparse.format(sql, output_format='python')
        assert f(sql) == "sql = 'select \\'\\\\foo\\\\\\''"

    def test_php_escapes_backslashes(self):
        # GHSA-3496-9g83-7v6x: PHP double-quoted output must escape backslashes
        # before quotes; a backslash before a quote otherwise closes the string.
        # SQL  select '\foo\'  -> each \ doubled (single quotes need no escaping).
        sql = "select '\\foo\\'"
        f = lambda sql: sqlparse.format(sql, output_format='php')
        assert f(sql) == '$sql = "select \'\\\\foo\\\\\'";'

    def test_sql(self):
        # "sql" is an allowed option but has no effect
        sql = 'select * from foo;'
        f = lambda sql: sqlparse.format(sql, output_format='sql')
        assert f(sql) == 'select * from foo;'

    def test_invalid_option(self):
        sql = 'select * from foo;'
        with pytest.raises(SQLParseError):
            sqlparse.format(sql, output_format='foo')


def test_format_column_ordering():
    # issue89
    sql = 'select * from foo order by c1 desc, c2, c3;'
    formatted = sqlparse.format(sql, reindent=True)
    expected = '\n'.join([
        'select *',
        'from foo',
        'order by c1 desc,',
        '         c2,',
        '         c3;'])
    assert formatted == expected


def test_truncate_strings():
    sql = "update foo set value = '{}';".format('x' * 1000)
    formatted = sqlparse.format(sql, truncate_strings=10)
    assert formatted == "update foo set value = 'xxxxxxxxxx[...]';"
    formatted = sqlparse.format(sql, truncate_strings=3, truncate_char='YYY')
    assert formatted == "update foo set value = 'xxxYYY';"


@pytest.mark.parametrize('option', ['bar', -1, 0])
def test_truncate_strings_invalid_option2(option):
    with pytest.raises(SQLParseError):
        sqlparse.format('foo', truncate_strings=option)


@pytest.mark.parametrize('sql', [
    'select verrrylongcolumn from foo',
    'select "verrrylongcolumn" from "foo"'])
def test_truncate_strings_doesnt_truncate_identifiers(sql):
    formatted = sqlparse.format(sql, truncate_strings=2)
    assert formatted == sql


def test_having_produces_newline():
    sql = ('select * from foo, bar where bar.id = foo.bar_id '
           'having sum(bar.value) > 100')
    formatted = sqlparse.format(sql, reindent=True)
    expected = [
        'select *',
        'from foo,',
        '     bar',
        'where bar.id = foo.bar_id',
        'having sum(bar.value) > 100']
    assert formatted == '\n'.join(expected)


@pytest.mark.parametrize('right_margin', ['ten', 2])
def test_format_right_margin_invalid_option(right_margin):
    with pytest.raises(SQLParseError):
        sqlparse.format('foo', right_margin=right_margin)


@pytest.mark.xfail(reason="Needs fixing")
def test_format_right_margin():
    # TODO: Needs better test, only raises exception right now
    sqlparse.format('foo', right_margin="79")


def test_format_json_ops():  # issue542
    formatted = sqlparse.format(
        "select foo->'bar', foo->'bar';", reindent=True)
    expected = "select foo->'bar',\n       foo->'bar';"
    assert formatted == expected


@pytest.mark.parametrize('sql, expected_normal, expected_compact', [
    ('case when foo then 1 else bar end',
     'case\n    when foo then 1\n    else bar\nend',
     'case when foo then 1 else bar end')])
def test_compact(sql, expected_normal, expected_compact):  # issue783
    formatted_normal = sqlparse.format(sql, reindent=True)
    formatted_compact = sqlparse.format(sql, reindent=True, compact=True)
    assert formatted_normal == expected_normal
    assert formatted_compact == expected_compact


def test_strip_ws_removes_trailing_ws_in_groups():  # issue782
    formatted = sqlparse.format('( where foo = bar  ) from',
                                strip_whitespace=True)
    expected = '(where foo = bar) from'
    assert formatted == expected
