-- Add nickname to user table
ALTER TABLE "public"."user"
ADD COLUMN "nickname" character varying(80);
