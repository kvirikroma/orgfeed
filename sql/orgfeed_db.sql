--
-- PostgreSQL database dump
--

-- Dumped from database version 11.10 (Ubuntu 11.10-1.pgdg18.04+1)
-- Dumped by pg_dump version 11.10 (Ubuntu 11.10-1.pgdg18.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid(); Type: FUNCTION; Schema: public; Owner: orgfeed_user
--

CREATE FUNCTION public.uuid() RETURNS uuid
    LANGUAGE sql
    AS $$SELECT uuid_in(md5(random()::text)::cstring)$$;


ALTER FUNCTION public.uuid() OWNER TO orgfeed_user;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: attachments; Type: TABLE; Schema: public; Owner: orgfeed_user
--

CREATE TABLE public.attachments (
    id uuid DEFAULT public.uuid() NOT NULL,
    author uuid NOT NULL,
    post uuid NOT NULL
);


ALTER TABLE public.attachments OWNER TO orgfeed_user;

--
-- Name: employees; Type: TABLE; Schema: public; Owner: orgfeed_user
--

CREATE TABLE public.employees (
    id uuid DEFAULT public.uuid() NOT NULL,
    full_name text NOT NULL,
    subunit uuid NOT NULL,
    user_type smallint DEFAULT 0 NOT NULL,
    fired boolean DEFAULT false NOT NULL,
    email text NOT NULL,
    password_hash text NOT NULL
);


ALTER TABLE public.employees OWNER TO orgfeed_user;

--
-- Name: posts; Type: TABLE; Schema: public; Owner: orgfeed_user
--

CREATE TABLE public.posts (
    id uuid DEFAULT public.uuid() NOT NULL,
    type smallint DEFAULT 0 NOT NULL,
    title text NOT NULL,
    created_on timestamp without time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    published_on timestamp without time zone,
    archived_on timestamp without time zone DEFAULT (timezone('utc'::text, now()) + '6 mons'::interval) NOT NULL,
    author uuid NOT NULL,
    approved_by uuid NOT NULL,
    status smallint DEFAULT 0 NOT NULL,
    body text NOT NULL
);


ALTER TABLE public.posts OWNER TO orgfeed_user;

--
-- Name: subunits; Type: TABLE; Schema: public; Owner: orgfeed_user
--

CREATE TABLE public.subunits (
    id uuid DEFAULT public.uuid() NOT NULL,
    name text NOT NULL,
    address text NOT NULL,
    leader uuid NOT NULL,
    email text NOT NULL,
    phone text NOT NULL
);


ALTER TABLE public.subunits OWNER TO orgfeed_user;

--
-- Name: attachments attachments_pkey; Type: CONSTRAINT; Schema: public; Owner: orgfeed_user
--

ALTER TABLE ONLY public.attachments
    ADD CONSTRAINT attachments_pkey PRIMARY KEY (id);


--
-- Name: employees employees_email_key; Type: CONSTRAINT; Schema: public; Owner: orgfeed_user
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_email_key UNIQUE (email);


--
-- Name: employees employees_pkey; Type: CONSTRAINT; Schema: public; Owner: orgfeed_user
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_pkey PRIMARY KEY (id);


--
-- Name: posts posts_pkey; Type: CONSTRAINT; Schema: public; Owner: orgfeed_user
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);


--
-- Name: subunits subunits_email_key; Type: CONSTRAINT; Schema: public; Owner: orgfeed_user
--

ALTER TABLE ONLY public.subunits
    ADD CONSTRAINT subunits_email_key UNIQUE (email);


--
-- Name: subunits subunits_name_key; Type: CONSTRAINT; Schema: public; Owner: orgfeed_user
--

ALTER TABLE ONLY public.subunits
    ADD CONSTRAINT subunits_name_key UNIQUE (name);


--
-- Name: subunits subunits_pkey; Type: CONSTRAINT; Schema: public; Owner: orgfeed_user
--

ALTER TABLE ONLY public.subunits
    ADD CONSTRAINT subunits_pkey PRIMARY KEY (id);


--
-- Name: attachments_author_idx; Type: INDEX; Schema: public; Owner: orgfeed_user
--

CREATE INDEX attachments_author_idx ON public.attachments USING btree (author);


--
-- Name: attachments_post_idx; Type: INDEX; Schema: public; Owner: orgfeed_user
--

CREATE INDEX attachments_post_idx ON public.attachments USING btree (post);


--
-- Name: employees_full_name_subunit_idx; Type: INDEX; Schema: public; Owner: orgfeed_user
--

CREATE INDEX employees_full_name_subunit_idx ON public.employees USING btree (full_name, subunit);


--
-- Name: employees_subunit_fired_user_type_idx; Type: INDEX; Schema: public; Owner: orgfeed_user
--

CREATE INDEX employees_subunit_fired_user_type_idx ON public.employees USING btree (subunit, fired, user_type);


--
-- Name: posts_status_author_published_on_created_on_idx; Type: INDEX; Schema: public; Owner: orgfeed_user
--

CREATE INDEX posts_status_author_published_on_created_on_idx ON public.posts USING btree (status, author, published_on, created_on);


--
-- Name: posts_title_idx; Type: INDEX; Schema: public; Owner: orgfeed_user
--

CREATE INDEX posts_title_idx ON public.posts USING btree (title);


--
-- Name: subunits_address_leader_phone_idx; Type: INDEX; Schema: public; Owner: orgfeed_user
--

CREATE INDEX subunits_address_leader_phone_idx ON public.subunits USING btree (address, leader, phone);


--
-- Name: attachments attachments_author_fkey; Type: FK CONSTRAINT; Schema: public; Owner: orgfeed_user
--

ALTER TABLE ONLY public.attachments
    ADD CONSTRAINT attachments_author_fkey FOREIGN KEY (author) REFERENCES public.employees(id);


--
-- Name: attachments attachments_post_fkey; Type: FK CONSTRAINT; Schema: public; Owner: orgfeed_user
--

ALTER TABLE ONLY public.attachments
    ADD CONSTRAINT attachments_post_fkey FOREIGN KEY (post) REFERENCES public.posts(id);


--
-- Name: employees employees_subunit_fkey; Type: FK CONSTRAINT; Schema: public; Owner: orgfeed_user
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_subunit_fkey FOREIGN KEY (subunit) REFERENCES public.subunits(id);


--
-- Name: posts posts_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: orgfeed_user
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.employees(id);


--
-- Name: posts posts_author_fkey; Type: FK CONSTRAINT; Schema: public; Owner: orgfeed_user
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_author_fkey FOREIGN KEY (author) REFERENCES public.employees(id);


--
-- Name: subunits subunits_leader_fkey; Type: FK CONSTRAINT; Schema: public; Owner: orgfeed_user
--

ALTER TABLE ONLY public.subunits
    ADD CONSTRAINT subunits_leader_fkey FOREIGN KEY (leader) REFERENCES public.employees(id);


--
-- PostgreSQL database dump complete
--

